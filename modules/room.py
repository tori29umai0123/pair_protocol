class Room:
    def __init__(self, id):
        self.id = id
        self.occupants = []  # Character オブジェクトのリスト
        self.roles = {}  # キャラクター名: ロール のマッピング

    def assign_pair(self, active_char, passive_char):
        """部屋に攻/受のペアを割り当て"""
        # 現在の住人をクリア
        self.clear_occupants()
        
        # 新しい住人を追加
        if active_char and passive_char:
            success_active = self.add_occupant(active_char, "active")
            success_passive = self.add_occupant(passive_char, "passive")
            return success_active and success_passive
        return False

    def add_occupant(self, character, role):
        """キャラクターを部屋に追加"""
        if len(self.occupants) < 2:
            # 既に同じキャラクターが他の役割で入っていないかチェック
            if character not in self.occupants:
                self.occupants.append(character)
                self.roles[character.name] = role
                character.assign_to_room(self.id, role)
                return True
        return False

    def remove_occupant(self, character):
        """キャラクターを部屋から削除"""
        if character in self.occupants:
            self.occupants.remove(character)
            if character.name in self.roles:
                del self.roles[character.name]
            character.remove_from_room()
            return True
        return False

    def clear_occupants(self):
        """全ての住人を削除"""
        for character in self.occupants[:]:  # リストのコピーを使用してイテレート
            character.remove_from_room()
        self.occupants = []
        self.roles = {}

    def get_occupant_by_role(self, role):
        """指定された役割のキャラクターを取得"""
        for character in self.occupants:
            if self.roles.get(character.name) == role:
                return character
        return None

    def is_full(self):
        """部屋が満員かどうかを確認"""
        return len(self.occupants) >= 2

    def is_empty(self):
        """部屋が空かどうかを確認"""
        return len(self.occupants) == 0