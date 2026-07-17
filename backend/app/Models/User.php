<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Foundation\Auth\User as Authenticatable;
use Illuminate\Notifications\Notifiable;
use Laravel\Sanctum\HasApiTokens;

class User extends Authenticatable
{
    use HasApiTokens, HasFactory, Notifiable;

    protected $fillable = [
        'username',
        'password',
        'name',
        'email',
        'avatar',
        'is_admin',
        'active',
        'expiry_date',
    ];

    protected $hidden = [
        'password',
        'remember_token',
    ];

    protected $casts = [
        'is_admin' => 'boolean',
        'active' => 'boolean',
        'expiry_date' => 'datetime',
        'last_login_at' => 'datetime',
        'password' => 'hashed',
    ];

    public function isAdmin(): bool
    {
        return $this->is_admin;
    }

    public function isExpired(): bool
    {
        return $this->expiry_date && $this->expiry_date->isPast();
    }
}
