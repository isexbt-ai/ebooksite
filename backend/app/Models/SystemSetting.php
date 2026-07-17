<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class SystemSetting extends Model
{
    use HasFactory;

    protected $table = 'system_settings';

    protected $fillable = [
        'key',
        'value',
    ];

    public static function get(string $key, string $default = ''): string
    {
        $setting = self::where('key', $key)->first();
        return $setting ? $setting->value : $default;
    }

    public static function set(string $key, string $value): void
    {
        self::updateOrCreate(['key' => $key], ['value' => $value]);
    }
}
