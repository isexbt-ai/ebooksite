<?php

namespace App\Services;

use Aws\S3\S3Client;
use Aws\Exception\AwsException;
use Illuminate\Support\Facades\Log;

class R2StorageService
{
    protected S3Client $client;
    protected string $bucket;
    protected int $presignedExpires;

    public function __construct()
    {
        $this->client = new S3Client([
            'version' => 'latest',
            'region'  => config('services.r2.region', 'auto'),
            'endpoint' => config('services.r2.endpoint'),
            'credentials' => [
                'key'    => config('services.r2.key'),
                'secret' => config('services.r2.secret'),
            ],
        ]);

        $this->bucket = config('services.r2.bucket');
        $this->presignedExpires = config('services.r2.presigned_expires', 3600);
    }

    public function upload(string $filePath, string $key, ?string $contentType = null): ?string
    {
        try {
            $params = [
                'Bucket' => $this->bucket,
                'Key'    => $key,
                'Body'   => fopen($filePath, 'r'),
            ];
            if ($contentType) {
                $params['ContentType'] = $contentType;
            }
            $this->client->putObject($params);
            return $this->getPublicUrl($key);
        } catch (AwsException $e) {
            Log::error('R2 upload failed: ' . $e->getMessage());
            return null;
        }
    }

    public function uploadContent(string $content, string $key, ?string $contentType = null): ?string
    {
        try {
            $params = [
                'Bucket' => $this->bucket,
                'Key'    => $key,
                'Body'   => $content,
            ];
            if ($contentType) {
                $params['ContentType'] = $contentType;
            }
            $this->client->putObject($params);
            return $this->getPublicUrl($key);
        } catch (AwsException $e) {
            Log::error('R2 upload content failed: ' . $e->getMessage());
            return null;
        }
    }

    public function delete(string $key): bool
    {
        try {
            $this->client->deleteObject([
                'Bucket' => $this->bucket,
                'Key'    => $key,
            ]);
            return true;
        } catch (AwsException $e) {
            Log::error('R2 delete failed: ' . $e->getMessage());
            return false;
        }
    }

    public function exists(string $key): bool
    {
        try {
            $this->client->headObject([
                'Bucket' => $this->bucket,
                'Key'    => $key,
            ]);
            return true;
        } catch (AwsException $e) {
            return false;
        }
    }

    public function getPublicUrl(string $key): string
    {
        $publicUrl = config('services.r2.public_url');
        if ($publicUrl) {
            return rtrim($publicUrl, '/') . '/' . ltrim($key, '/');
        }
        return $this->client->getObjectUrl($this->bucket, $key);
    }

    public function getPresignedUrl(string $key, ?int $expires = null): ?string
    {
        $expires = $expires ?? $this->presignedExpires;
        try {
            $cmd = $this->client->createPresignedRequest(
                $this->client->getCommand('GetObject', [
                    'Bucket' => $this->bucket,
                    'Key'    => $key,
                ]),
                "+{$expires} seconds"
            );
            return (string) $cmd->getUri();
        } catch (AwsException $e) {
            Log::error('R2 presigned URL failed: ' . $e->getMessage());
            return null;
        }
    }

    public function initiateMultipartUpload(string $key, ?string $contentType = null): ?string
    {
        try {
            $params = [
                'Bucket' => $this->bucket,
                'Key'    => $key,
            ];
            if ($contentType) {
                $params['ContentType'] = $contentType;
            }
            $result = $this->client->createMultipartUpload($params);
            return $result['UploadId'];
        } catch (AwsException $e) {
            Log::error('R2 initiate multipart upload failed: ' . $e->getMessage());
            return null;
        }
    }

    public function uploadPart(string $key, string $uploadId, int $partNumber, string $content, string $contentMd5): ?array
    {
        try {
            $result = $this->client->uploadPart([
                'Bucket'     => $this->bucket,
                'Key'        => $key,
                'UploadId'   => $uploadId,
                'PartNumber' => $partNumber,
                'Body'       => $content,
                'ContentMD5' => $contentMd5,
            ]);
            return [
                'ETag'       => $result['ETag'],
                'PartNumber' => $partNumber,
            ];
        } catch (AwsException $e) {
            Log::error('R2 upload part failed: ' . $e->getMessage());
            return null;
        }
    }

    public function completeMultipartUpload(string $key, string $uploadId, array $parts): ?string
    {
        try {
            $this->client->completeMultipartUpload([
                'Bucket'   => $this->bucket,
                'Key'      => $key,
                'UploadId' => $uploadId,
                'MultipartUpload' => [
                    'Parts' => $parts,
                ],
            ]);
            return $this->getPublicUrl($key);
        } catch (AwsException $e) {
            Log::error('R2 complete multipart upload failed: ' . $e->getMessage());
            return null;
        }
    }

    public function abortMultipartUpload(string $key, string $uploadId): bool
    {
        try {
            $this->client->abortMultipartUpload([
                'Bucket'   => $this->bucket,
                'Key'      => $key,
                'UploadId' => $uploadId,
            ]);
            return true;
        } catch (AwsException $e) {
            Log::error('R2 abort multipart upload failed: ' . $e->getMessage());
            return false;
        }
    }

    public function listObjects(string $prefix = '', int $maxKeys = 1000): array
    {
        try {
            $result = $this->client->listObjectsV2([
                'Bucket'  => $this->bucket,
                'Prefix'  => $prefix,
                'MaxKeys' => $maxKeys,
            ]);
            return $result['Contents'] ?? [];
        } catch (AwsException $e) {
            Log::error('R2 list objects failed: ' . $e->getMessage());
            return [];
        }
    }
}
