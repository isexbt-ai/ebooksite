<?php

namespace App\Services;

use Illuminate\Http\JsonResponse;

/**
 * 统一API响应服务
 * 格式: {code: 0, data: {}, message: ''}
 * code=0 表示成功，非0为错误码
 */
class ApiResponseService
{
    public function success(mixed $data = null, string $message = '操作成功', int $httpCode = 200): JsonResponse
    {
        return response()->json([
            'code' => 0,
            'data' => $data,
            'message' => $message,
        ], $httpCode);
    }

    public function error(string $message = '操作失败', int $code = 1, int $httpCode = 400): JsonResponse
    {
        return response()->json([
            'code' => $code,
            'data' => null,
            'message' => $message,
        ], $httpCode);
    }

    public function notFound(string $message = '资源不存在'): JsonResponse
    {
        return $this->error($message, 404, 404);
    }

    public function forbidden(string $message = '无权限访问'): JsonResponse
    {
        return $this->error($message, 403, 403);
    }

    public function unauthorized(string $message = '未登录或登录已过期'): JsonResponse
    {
        return $this->error($message, 401, 401);
    }

    public function validationError(string $message = '参数验证失败', int $code = 422): JsonResponse
    {
        return $this->error($message, $code, 422);
    }

    public function paginate($paginator, string $message = '获取成功'): JsonResponse
    {
        return $this->success([
            'total' => $paginator->total(),
            'items' => $paginator->items(),
            'page' => $paginator->currentPage(),
            'size' => $paginator->perPage(),
        ], $message);
    }
}
