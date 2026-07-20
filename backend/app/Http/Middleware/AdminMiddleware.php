<?php

namespace App\Http\Middleware;

use Closure;
use Illuminate\Http\Request;
use Symfony\Component\HttpFoundation\Response;

class AdminMiddleware
{
    /**
     * 验证用户是否为管理员
     */
    public function handle(Request $request, Closure $next): Response
    {
        if (!$request->user() || !$request->user()->is_admin) {
            return response()->json([
                'code'    => 403,
                'data'    => null,
                'message' => '需要管理员权限',
            ], 403);
        }

        return $next($request);
    }
}
