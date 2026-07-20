<?php

namespace App\Http\Controllers;

use App\Models\User;
use App\Models\Card;
use App\Models\AuditLog;
use Illuminate\Http\Request;
use Illuminate\Http\JsonResponse;
use Illuminate\Support\Facades\Hash;
use Illuminate\Support\Str;

class AuthController extends Controller
{
    /**
     * 用户注册
     */
    public function register(Request $request): JsonResponse
    {
        $validated = $request->validate([
            'username'  => 'required|string|min:3|max:50|unique:users,username',
            'password'  => 'required|string|min:8|regex:/^(?=.*[A-Za-z])(?=.*\d).+$/',
            'card_code' => 'required|string',
        ], [
            'password.regex' => '密码必须包含字母和数字',
            'password.min'   => '密码至少8位',
        ]);

        $card = Card::where('code', $validated['card_code'])->first();

        if (!$card) {
            return $this->api->error('卡密无效', 1001);
        }

        if ($card->used) {
            return $this->api->error('卡密已被使用', 1002);
        }

        if ($card->isExpired()) {
            return $this->api->error('卡密已过期', 1003);
        }

        $user = User::create([
            'username'    => strtolower($validated['username']),
            'password'    => Hash::make($validated['password']),
            'name'        => $validated['username'],
            'active'      => true,
            'expiry_date' => now()->addDays($card->duration_days),
        ]);

        $card->update([
            'used'    => true,
            'used_by' => $user->id,
            'used_at' => now(),
        ]);

        AuditLog::log('register', 'user', $user->id);

        return $this->api->success([
            'user_id'     => $user->id,
            'username'    => $user->username,
            'expiry_date' => $user->expiry_date,
        ], '注册成功', 201);
    }

    /**
     * 用户登录
     */
    public function login(Request $request): JsonResponse
    {
        $validated = $request->validate([
            'username' => 'required|string',
            'password' => 'required|string',
        ]);

        $user = User::where('username', strtolower($validated['username']))->first();

        if (!$user || !Hash::check($validated['password'], $user->password)) {
            return $this->api->error('用户名或密码错误', 1010);
        }

        if (!$user->active) {
            return $this->api->error('账号未激活', 1011);
        }

        if ($user->isExpired()) {
            return $this->api->error('账号已过期，请续费', 1012);
        }

        $user->update(['last_login_at' => now()]);

        $token = $user->createToken('api')->plainTextToken;

        return $this->api->success([
            'user_id'     => $user->id,
            'username'    => $user->username,
            'name'        => $user->name,
            'admin'       => $user->is_admin,
            'expiry_date' => $user->expiry_date,
            'token'       => $token,
        ], '登录成功');
    }

    /**
     * 管理员登录
     */
    public function adminLogin(Request $request): JsonResponse
    {
        $validated = $request->validate([
            'username' => 'required|string',
            'password' => 'required|string',
        ]);

        $user = User::where('username', strtolower($validated['username']))->first();

        if (!$user || !Hash::check($validated['password'], $user->password)) {
            return $this->api->error('用户名或密码错误', 1010);
        }

        if (!$user->is_admin) {
            return $this->api->forbidden('需要管理员权限');
        }

        $user->update(['last_login_at' => now()]);

        $token = $user->createToken('admin')->plainTextToken;

        AuditLog::log('admin_login', 'user', $user->id);

        return $this->api->success([
            'user_id'  => $user->id,
            'username' => $user->username,
            'name'     => $user->name,
            'admin'    => true,
            'token'    => $token,
        ], '登录成功');
    }

    /**
     * 用户登出
     */
    public function logout(Request $request): JsonResponse
    {
        $request->user()->currentAccessToken()->delete();
        return $this->api->success(null, '已登出');
    }

    /**
     * 获取当前用户信息
     */
    public function me(Request $request): JsonResponse
    {
        $user = $request->user();
        return $this->api->success([
            'id'          => $user->id,
            'username'    => $user->username,
            'name'        => $user->name,
            'email'       => $user->email,
            'avatar'      => $user->avatar,
            'admin'       => $user->is_admin,
            'active'      => $user->active,
            'expiry_date' => $user->expiry_date,
            'created_at'  => $user->created_at,
        ]);
    }

    /**
     * 卡密兑换
     */
    public function redeem(Request $request): JsonResponse
    {
        $validated = $request->validate([
            'card_code' => 'required|string',
        ]);

        $card = Card::where('code', $validated['card_code'])->first();

        if (!$card) {
            return $this->api->error('卡密无效', 1001);
        }

        if ($card->used) {
            return $this->api->error('卡密已被使用', 1002);
        }

        if ($card->isExpired()) {
            return $this->api->error('卡密已过期', 1003);
        }

        $user = $request->user();

        $currentExpiry = $user->expiry_date ?? now();
        $newExpiry = $currentExpiry->addDays($card->duration_days);
        $user->update(['expiry_date' => $newExpiry]);

        $card->update([
            'used'    => true,
            'used_by' => $user->id,
            'used_at' => now(),
        ]);

        AuditLog::log('redeem_card', 'card', $card->id);

        return $this->api->success([
            'duration_days'  => $card->duration_days,
            'new_expiry_date' => $newExpiry,
        ], '兑换成功');
    }

    /**
     * 生成卡密代码 - 统一4段4位大写字母格式
     */
    private function generateCardCode(): string
    {
        $parts = [];
        for ($i = 0; $i < 4; $i++) {
            $parts[] = Str::upper(Str::random(4));
        }
        return implode('-', $parts);
    }
}
