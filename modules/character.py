class Character:
    def __init__(self, data):
        self.name = data["name"]
        self.name_en = data["name_en"]
        self.gender = data["gender"]
        self.type = data["type"]
        self.background = data["background"]
        self.personality = data["personality"]
        self.room = None
        self.room_role = None
        self.love_values = {}
        self.hate_values = {}
        self.emotion_reasons = {
            "love": {},
            "hate": {}
        }
        
        # 初期感情値と理由の設定
        if "initial_emotions" in data:
            for emotion_type, emotions in data["initial_emotions"].items():
                for target, info in emotions.items():
                    if emotion_type == "love":
                        self.love_values[target] = info["value"]
                        self.emotion_reasons["love"][target] = info["reason"]
                    elif emotion_type == "hate":
                        self.hate_values[target] = info["value"]
                        self.emotion_reasons["hate"][target] = info["reason"]
        
        # その他の属性
        self.active_behavior = data.get("active_behavior", "")
        self.passive_behavior = data.get("passive_behavior", "")
        self.values = data.get("values", {})
        self.speech_pattern = data.get("speech_pattern", {})
        self.emotion_expression = data.get("emotion_expression", {})
        self.behavior_habits = data.get("behavior_habits", [])
        self.intimacy_progression = data.get("intimacy_progression", "")
        
        # 初期感情値と理由の設定
        if "initial_emotions" in data:
            for emotion_type, emotions in data["initial_emotions"].items():
                for target, info in emotions.items():
                    if emotion_type == "love":
                        self.love_values[target] = info["value"]
                        self.emotion_reasons["love"][target] = info["reason"]
                    elif emotion_type == "hate":
                        self.hate_values[target] = info["value"]
                        self.emotion_reasons["hate"][target] = info["reason"]
        
        # その他の属性
        self.active_behavior = data.get("active_behavior", "")
        self.passive_behavior = data.get("passive_behavior", "")
        self.values = data.get("values", {})
        self.speech_pattern = data.get("speech_pattern", {})
        self.emotion_expression = data.get("emotion_expression", {})
        self.behavior_habits = data.get("behavior_habits", [])
        self.intimacy_progression = data.get("intimacy_progression", "")

    def assign_to_room(self, room_id, role):
        """部屋への割り当てを設定"""
        self.room = room_id
        self.room_role = role

    def remove_from_room(self):
        """部屋の割り当てを解除"""
        self.room = None
        self.room_role = None


    def get_emotion_reason(self, target, emotion_type):
        """特定のキャラクターに対する感情の理由を取得"""
        return self.emotion_reasons[emotion_type].get(target, "理由不明")
    
    def update_emotion(self, target, love_change, hate_change, reason=""):
        """感情値を更新し、新しい理由を設定"""
        if target in self.love_values:
            self.love_values[target] = max(0, min(100, self.love_values[target] + love_change))
            if reason:
                self.emotion_reasons["love"][target] = reason
        
        if target in self.hate_values:
            self.hate_values[target] = max(0, min(100, self.hate_values[target] + hate_change))
            if reason:
                self.emotion_reasons["hate"][target] = reason
    
    def get_emotion_density(self, target):
        """特定の相手との感情密度を計算する"""
        love = self.love_values.get(target, 0)
        hate = self.hate_values.get(target, 0)
        return abs(love) + abs(hate)  # 感情密度は愛情と憎悪の絶対値の合計
    
    def to_dict(self):
        """キャラクター情報を辞書形式で返す"""
        return {
            "name": self.name,
            "name_en": self.name_en,
            "gender": self.gender,
            "type": self.type,
            "background": self.background,
            "personality": self.personality,
            "love_values": self.love_values,
            "hate_values": self.hate_values,
            "room": self.room,
            "room_role": self.room_role,
            "active_behavior": self.active_behavior,
            "passive_behavior": self.passive_behavior,
            "values": self.values,
            "speech_pattern": self.speech_pattern,
            "emotion_expression": self.emotion_expression,
            "behavior_habits": self.behavior_habits,
            "intimacy_progression": self.intimacy_progression
        }