<?php

namespace App\Http\Controllers;

use App\Models\Setting;
use App\Models\Feedback;
use Illuminate\Http\Request;
use Illuminate\Http\JsonResponse;

class SettingsController extends Controller
{
    /**
     * 获取公开设置
     */
    public function index(): JsonResponse
    {
        $publicKeys = ['site_name', 'site_description', 'buy_link', 'book_count_display', 'download_limit', 'video_link', 'game_link'];
        $settings = [];

        foreach ($publicKeys as $key) {
            $value = Setting::get($key);
            if ($value !== null) {
                $settings[$key] = $value;
            }
        }

        return $this->api->success($settings);
    }

    /**
     * 提交反馈
     */
    public function feedback(Request $request): JsonResponse
    {
        $validated = $request->validate([
            'content' => 'required|string|max:2000',
            'contact' => 'nullable|string|max:200',
        ]);

        $userId = $request->user() ? $request->user()->id : null;

        Feedback::create([
            'user_id' => $userId,
            'content' => $validated['content'],
            'contact' => $validated['contact'] ?? '',
        ]);

        return $this->api->success(null, '反馈提交成功', 201);
    }
}
