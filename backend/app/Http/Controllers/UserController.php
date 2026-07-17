<?php

namespace App\Http\Controllers;

use App\Models\User;
use Illuminate\Http\Request;
use Illuminate\Http\JsonResponse;
use Illuminate\Support\Facades\Hash;

class UserController extends Controller
{
    /**
     * 更新用户资料
     */
    public function updateProfile(Request $request): JsonResponse
    {
        $validated = $request->validate([
            'name' => 'nullable|string',
            'email' => 'nullable|email',
        ]);

        $user = $request->user();
        $user->update($validated);

        return response()->json(['err' => 'ok']);
    }

    /**
     * 修改密码
     */
    public function changePassword(Request $request): JsonResponse
    {
        $validated = $request->validate([
            'old_password' => 'required|string',
            'new_password' => 'required|string|min:6|max:20',
        ]);

        $user = $request->user();

        if (!Hash::check($validated['old_password'], $user->password)) {
            return response()->json(['err' => 'invalid_password', 'msg' => '旧密码错误'], 400);
        }

        $user->update(['password' => Hash::make($validated['new_password'])]);

        return response()->json(['err' => 'ok']);
    }
}
