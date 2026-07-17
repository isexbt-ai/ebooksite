<?php

namespace App\Http\Controllers;

use App\Models\User;
use App\Models\Card;
use App\Models\SystemSetting;
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
            'username' => 'required|string|min:3|max:50|unique:users,username',
            'password' => 'required|string|min:6|max:20',
            'card_code' => 'required|string',
        ]);

        $card = Card::where('code', $validated['card_code'])->first();

        if (!$card) {
            return response()->json(['err' => 'invalid_card', 'msg' => '卡密无效'], 400);
        }

        if ($card->used) {
            return response()->json(['err' => 'card_used', 'msg' => '卡密已被使用'], 400);
        }

        if ($card->isExpired()) {
            return response()->json(['err' => 'card_expired', 'msg' => '卡密已过期'], 400);
        }

        $user = User::create([
            'username' => strtolower($validated['username']),
            'password' => Hash::make($validated['password']),
            'name' => $validated['username'],
            'active' => true,
            'expiry_date' => now()->addDays($card->duration_days),
        ]);

        $card->update([
            'used' => true,
            'used_by' => $user->id,
            'used_at' => now(),
        ]);

        return response()->json([
            'err' => 'ok',
            'data' => [
                'user_id' => $user->id,
                'username' => $user->username,
                'expiry_date' => $user->expiry_date,
            ],
        ]);
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
            return response()->json(['err' => 'invalid_credentials', 'msg' => '用户名或密码错误'], 400);
        }

        if (!$user->active) {
            return response()->json(['err' => 'account_inactive', 'msg' => '账号未激活'], 400);
        }

        if ($user->isExpired()) {
            return response()->json(['err' => 'account_expired', 'msg' => '账号已过期，请续费'], 400);
        }

        $user->update(['last_login_at' => now()]);

        $token = $user->createToken('api')->plainTextToken;

        return response()->json([
            'err' => 'ok',
            'data' => [
                'user_id' => $user->id,
                'username' => $user->username,
                'name' => $user->name,
                'admin' => $user->is_admin,
                'expiry_date' => $user->expiry_date,
                'token' => $token,
            ],
        ]);
    }

    /**
     * 用户登出
     */
    public function logout(Request $request): JsonResponse
    {
        $request->user()->currentAccessToken()->delete();
        return response()->json(['err' => 'ok']);
    }

    /**
     * 获取当前用户信息
     */
    public function me(Request $request): JsonResponse
    {
        $user = $request->user();
        return response()->json([
            'err' => 'ok',
            'data' => [
                'id' => $user->id,
                'username' => $user->username,
                'name' => $user->name,
                'email' => $user->email,
                'avatar' => $user->avatar,
                'admin' => $user->is_admin,
                'active' => $user->active,
                'expiry_date' => $user->expiry_date,
                'created_at' => $user->created_at,
            ],
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
            return response()->json(['err' => 'invalid_card', 'msg' => '卡密无效'], 400);
        }

        if ($card->used) {
            return response()->json(['err' => 'card_used', 'msg' => '卡密已被使用'], 400);
        }

        if ($card->isExpired()) {
            return response()->json(['err' => 'card_expired', 'msg' => '卡密已过期'], 400);
        }

        $user = $request->user();

        // 延长有效期
        $currentExpiry = $user->expiry_date ?? now();
        $newExpiry = $currentExpiry->addDays($card->duration_days);
        $user->update(['expiry_date' => $newExpiry]);

        $card->update([
            'used' => true,
            'used_by' => $user->id,
            'used_at' => now(),
        ]);

        return response()->json([
            'err' => 'ok',
            'data' => [
                'duration_days' => $card->duration_days,
                'new_expiry_date' => $newExpiry,
            ],
        ]);
    }

    /**
     * 生成卡密（管理员）
     */
    public function generateCards(Request $request): JsonResponse
    {
        $validated = $request->validate([
            'count' => 'required|integer|min:1|max:100',
            'type' => 'required|string|in:register,renew',
            'duration_days' => 'required|integer|min:1|max:3650',
        ]);

        $codes = [];
        for ($i = 0; $i < $validated['count']; $i++) {
            $code = $this->generateCardCode();
            Card::create([
                'code' => $code,
                'type' => $validated['type'],
                'duration_days' => $validated['duration_days'],
            ]);
            $codes[] = $code;
        }

        return response()->json([
            'err' => 'ok',
            'data' => [
                'codes' => $codes,
                'count' => count($codes),
                'type' => $validated['type'],
                'duration_days' => $validated['duration_days'],
            ],
        ]);
    }

    /**
     * 生成卡密代码
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
