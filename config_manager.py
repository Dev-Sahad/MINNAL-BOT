# =============================================================================
#  config_manager.py — Live Settings Manager
#  Real-time configuration system for MINNAL Bot
# =============================================================================

import json
import os
from datetime import datetime
from typing import Any, Dict


class ConfigManager:
    """Manages live bot configuration with auto-save and backup"""
    
    def __init__(self):
        self.data_dir = "data"
        self.config_file = os.path.join(self.data_dir, "settings.json")
        self.backup_file = os.path.join(self.data_dir, "settings_backup.json")
        
        # Ensure data directory exists
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
        
        # Load or create config
        self.config = self.load_config()
    
    def get_default_config(self) -> Dict[str, Any]:
        """Default configuration values"""
        return {
            "_meta": {
                "version": "1.0",
                "last_updated": datetime.utcnow().isoformat(),
                "updated_by": "system"
            },
            
            # Bot Settings
            "bot": {
                "name": "MINNAL",
                "tagline": "The Unlimited Lightning Engine",
                "developer": "@sxhd_sha",
                "color_theme": "purple",
                "embed_color": "#9b59b6"
            },
            
            # Welcome System
            "welcome": {
                "enabled": True,
                "channel_id": 1463854523935359115,
                "title": "**✨ WELCOME TO THE ENVIRONMENT**",
                "message": (
                    "**`|`** 👋 **IDENTITY:** {member}\n"
                    "**`|`** 📑 **REGISTRY:** `Member #{member guild.member_count}`\n"
                    "**`|`** 📡 **LOCATION:** `{member guild.name}`\n\n"
                    "**`|`** 📜 **CORE PROTOCOLS:**\n"
                    "**`|`** 1️⃣ Read the ` #rules `\n"
                    "**`|`** 2️⃣ Assign ` #roles `\n"
                    "**`|`** 3️⃣ Initialize in ` #general `\n\n"
                    "**` STATUS: ACCESS GRANTED `**"
                ),
                "image_url": "",
                "color": "gold",
                "send_dm": True,
                "dm_message": "Welcome to {server}, {member}! Type /help to see what I can do."
            },
            
            # Goodbye System
            "goodbye": {
                "enabled": True,
                "channel_id": 1463855462712868948,
                "title": "💔 **A MEMBER HAS DEPARTED**",
                "message": (
                    "**`|`** 👤 **IDENTITY:** `{member.name}`\n"
                    "**`|`** 🆔 **SERIAL:** `{member.id}`\n"
                    "**`|`** 📉 **CAPACITY:** `{member guild.member_count}`\n\n"
                    "**`|`** 🕊️ *Safe travels through the network...*\n"
                    "**`|`** *We hope to see you back soon.* ✨\n\n"
                    "**` STATUS: SESSION TERMINATED `**"
                ),
                "color": "red"
            },
            
            # Summon Domain System
            "summon_domain": {
                "enabled": True,
                "trigger_channel_id": 0,
                "domain_names": [
                    "⚡ Minnal Cave",
                    "🩸 Sukuna's Shrine",
                    "🌀 Gojo's Infinity",
                    "🔥 Itadori's Pit",
                    "🌙 Megumi's Realm",
                    "💀 Mahito's Domain",
                    "⚔️ Yuta's Sanctuary",
                    "🌸 Nobara's Garden",
                    "🦊 Kurama's Den",
                    "🍜 Naruto's Rasengan",
                    "💥 Sasuke's Chidori",
                    "👁️ Tobi's Void",
                    "🐉 Akatsuki Hideout",
                    "❄️ Aizen's Throne",
                    "🌊 Luffy's Sunny",
                    "⚡ Zeus's Olympus",
                    "🌑 Madara's Tomb",
                    "🔮 Saitama's Cave",
                    "🗡️ Tanjiro's Forge",
                    "👾 Bankai: Katen Kyōkotsu: Karamatsu Shinjū",
                    "🌪️ Naruto's Vortex"
                ],
                "auto_delete": True,
                "send_notification": True
            },
            
            # Rizz Engine - Dynamic Bio
            "rizz_engine": {
                "enabled": True,
                "rotation_minutes": 5,
                "statuses": [
                    {"type": "watching", "name": "⚡ High Voltage [Server](https://discord.gg/3cQcMpcjRA)"},
                    {"type": "watching", "name": "🌀 Domain Expansions: Infinite void !"},
                    {"type": "watching", "name": "🩸 Sukuna's Throne"},
                    {"type": "watching", "name": "💻 Sahad's Code"},
                    {"type": "watching", "name": "🔥 Lightning Strike"},
                    {"type": "watching", "name": "👑 The Strongest"},
                    {"type": "playing", "name": "⚡ /help | MINNAL"},
                    {"type": "playing", "name": "🎮 with Lightning"},
                    {"type": "playing", "name": "💀 Cursed Energy"},
                    {"type": "playing", "name": "🌪️ Six Eyes"},
                    {"type": "playing", "name": "⚔️ Limitless Power"},
                    {"type": "listening", "name": "🎵 Anime OSTs"},
                    {"type": "listening", "name": "👂 Your Commands"},
                    {"type": "listening", "name": "🔊 The Voice of Sahad"},
                    {"type": "listening", "name": "⚡ Thunder Strikes"},
                    {"type": "competing", "name": "🏆 The Anime World"},
                    {"type": "competing", "name": "⚡ The Strongest Tournament"},
                    {"type": "competing", "name": "🎯 Code Optimization"}
                ]
            },
            
            # Economy System
            "economy": {
                "enabled": True,
                "currency_name": "Lightning Coins",
                "currency_symbol": "⚡",
                "starting_balance": 100,
                "daily_reward": 100,
                "weekly_reward": 1000,
                "max_balance": 1000000,
                "leaderboard_size": 10
            },
            
            # Ticket System
            "tickets": {
                "staff_role_ids": [1477254538313470096, 1499490549621850184],
                "log_channel_id": 1500510668418191510
            },
            
            # Game Updates
            "game_updates": {
                "enabled": True,
                "channel_id": 1467730984723284141,
                "hour": 9,
                "title": "🎮 Daily Game Update",
                "message": "Here's your daily gaming news!"
            },
            
            # Music Settings
            "music": {
                "enabled": True,
                "default_source": "soundcloud",
                "max_queue_size": 50,
                "auto_disconnect_minutes": 5,
                "volume_default": 50
            },
            
            # Web Panel
            "web_panel": {
                "enabled": True,
                "password_hash": "MINNAL@2025",  # In production, use proper hashing
                "panel_title": "MINNAL Admin Panel",
                "show_stats": True,
                "show_logs": False
            },
            
            # Custom Messages
            "custom_messages": {
                "level_up": "🎉 {member} leveled up to **Level {level}**!",
                "daily_claim": "💰 You received **{amount} {currency}**!",
                "command_disabled": "❌ This command is currently disabled.",
                "permission_denied": "⛔ You don't have permission for this!"
            },
            
            # Embed Templates
            "embeds": {
                "default_color": "#9b59b6",
                "success_color": "#2ecc71",
                "error_color": "#e74c3c",
                "warning_color": "#f1c40f",
                "info_color": "#3498db"
            }
        }
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from file or create default"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    print(f"✅ Loaded config from {self.config_file}", flush=True)
                    return config
            else:
                # Create default config
                default = self.get_default_config()
                self.save_config(default)
                print(f"📝 Created default config at {self.config_file}", flush=True)
                return default
        except Exception as e:
            print(f"❌ Error loading config: {e}", flush=True)
            return self.get_default_config()
    
    def save_config(self, config: Dict[str, Any] = None) -> bool:
        """Save configuration to file"""
        try:
            if config is None:
                config = self.config
            
            # Update metadata
            if "_meta" not in config:
                config["_meta"] = {}
            config["_meta"]["last_updated"] = datetime.utcnow().isoformat()
            
            # Backup current config
            if os.path.exists(self.config_file):
                try:
                    with open(self.config_file, 'r', encoding='utf-8') as f:
                        backup = f.read()
                    with open(self.backup_file, 'w', encoding='utf-8') as f:
                        f.write(backup)
                except Exception:
                    pass  # Backup failed, but continue
            
            # Save new config
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
            
            self.config = config
            print(f"✅ Config saved to {self.config_file}", flush=True)
            return True
        except Exception as e:
            print(f"❌ Error saving config: {e}", flush=True)
            return False
    
    def get(self, path: str, default=None):
        """Get value from config using dot notation
        Example: get('welcome.channel_id')
        """
        try:
            keys = path.split('.')
            value = self.config
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, path: str, value: Any) -> bool:
        """Set value in config using dot notation
        Example: set('welcome.channel_id', 1234567890)
        """
        try:
            keys = path.split('.')
            target = self.config
            
            # Navigate to parent
            for key in keys[:-1]:
                if key not in target:
                    target[key] = {}
                target = target[key]
            
            # Set value
            target[keys[-1]] = value
            
            # Auto-save
            self.save_config()
            return True
        except Exception as e:
            print(f"❌ Error setting {path}: {e}", flush=True)
            return False
    
    def update_section(self, section: str, data: Dict[str, Any]) -> bool:
        """Update entire section of config"""
        try:
            if section not in self.config:
                self.config[section] = {}
            
            self.config[section].update(data)
            self.save_config()
            return True
        except Exception as e:
            print(f"❌ Error updating section {section}: {e}", flush=True)
            return False
    
    def reload(self):
        """Reload config from file"""
        self.config = self.load_config()
    
    def get_all(self) -> Dict[str, Any]:
        """Get entire config"""
        return self.config
    
    def reset_section(self, section: str) -> bool:
        """Reset a section to defaults"""
        try:
            defaults = self.get_default_config()
            if section in defaults:
                self.config[section] = defaults[section]
                self.save_config()
                return True
            return False
        except Exception:
            return False
    
    def add_to_list(self, path: str, item: Any) -> bool:
        """Add item to a list in config"""
        try:
            current = self.get(path, [])
            if not isinstance(current, list):
                return False
            current.append(item)
            return self.set(path, current)
        except Exception:
            return False
    
    def remove_from_list(self, path: str, item: Any) -> bool:
        """Remove item from a list in config"""
        try:
            current = self.get(path, [])
            if not isinstance(current, list):
                return False
            if item in current:
                current.remove(item)
                return self.set(path, current)
            return False
        except Exception:
            return False


# Global instance - import this in cogs!
config = ConfigManager()


# Convenience functions
def get_setting(path: str, default=None):
    """Get a setting from config"""
    return config.get(path, default)


def set_setting(path: str, value: Any) -> bool:
    """Set a setting in config"""
    return config.set(path, value)


def reload_config():
    """Reload config from file"""
    config.reload()
