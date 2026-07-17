<?php

namespace App\Http\Controllers;

use App\Models\SystemSetting;
use App\Models\Feedback;
use Illuminate\Http\Request;
use Illuminate\Http\JsonResponse;

class SettingsController extends Controller
{
    /**
     * 获取购买链接
     */
    public function buyLink(): JsonResponse
    {
        $url = SystemSetting::get('buy_link', '');
        $bookCountDisplay = SystemSetting::get('book_count_display', '');

        return response()->json([
            'err' => 'ok',
            'data' => [
                'url' => $url,
                'book_count_display' => $bookCountDisplay,
            ],
        ]);
    }

    /**
     * 保存购买链接
     */
    public function saveBuyLink(Request $request): JsonResponse
    {
        $validated = $request->validate([
            'url' => 'nullable|string',
            'book_count_display' => 'nullable|string',
        ]);

        SystemSetting::set('buy_link', $validated['url'] ?? '');
        SystemSetting::set('book_count_display', $validated['book_count_display'] ?? '');

        return response()->json(['err' => 'ok']);
    }

    /**
     * 提交反馈
     */
    public function feedback(Request $request): JsonResponse
    {
        $validated = $request->validate([
            'content' => 'required|string',
            'contact' => 'nullable|string',
        ]);

        $userId = $request->user() ? $request->user()->id : null;

        Feedback::create([
            'user_id' => $userId,
            'content' => $validated['content'],
            'contact' => $validated['contact'] ?? '',
        ]);

        return response()->json(['err' => 'ok']);
    }
}
