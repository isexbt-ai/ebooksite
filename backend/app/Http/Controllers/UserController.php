<?php

namespace App\Http\Controllers;

use App\Models\Download;
use Illuminate\Http\Request;
use Illuminate\Http\JsonResponse;
use Illuminate\Support\Facades\Hash;

class UserController extends Controller
{
    /**
     * 获取用户资料
     */
    public function profile(Request $request): JsonResponse
    {
        $user = $request->user();
        return $this->api->success([
            'id'          => $user->id,
            'username'    => $user->username,
            'name'        => $user->name,
            'email'       => $user->email,
            'avatar'      => $user->avatar,
            'expiry_date' => $user->expiry_date,
            'created_at'  => $user->created_at,
        ]);
    }

    /**
     * 更新用户资料
     */
    public function updateProfile(Request $request): JsonResponse
    {
        $validated = $request->validate([
            'name'  => 'nullable|string|max:100',
            'email' => 'nullable|email|max:200',
        ]);

        $user = $request->user();
        $user->update($validated);

        return $this->api->success(null, '更新成功');
    }

    /**
     * 修改密码
     */
    public function changePassword(Request $request): JsonResponse
    {
        $validated = $request->validate([
            'old_password' => 'required|string',
            'new_password' => 'required|string|min:8|regex:/^(?=.*[A-Za-z])(?=.*\d).+$/',
        ], [
            'new_password.regex' => '密码必须包含字母和数字',
            'new_password.min'   => '密码至少8位',
        ]);

        $user = $request->user();

        if (!Hash::check($validated['old_password'], $user->password)) {
            return $this->api->error('旧密码错误', 1013);
        }

        $user->update(['password' => Hash::make($validated['new_password'])]);

        return $this->api->success(null, '密码修改成功');
    }

    /**
     * 下载记录
     */
    public function downloads(Request $request): JsonResponse
    {
        $page = $request->get('page', 1);
        $size = $request->get('size', 20);

        $downloads = Download::where('user_id', $request->user()->id)
            ->with('book:id,title,author,file_format,file_size')
            ->orderBy('created_at', 'desc')
            ->paginate($size, ['*'], 'page', $page);

        return $this->api->paginate($downloads);
    }
}
