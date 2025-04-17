import os
import json
import pickle
from datetime import datetime
from modules.room import Room 

class GameState:
    def __init__(self):
        self.turn = 1  # 1-5ターン
        self.phase = 1  # 1:部屋割り、2:共同生活、3:ワークショップ、4:感情スキャン
        self.characters = {}  # キャラクター名: Characterオブジェクト
        self.rooms = {}  # 部屋ID: Roomオブジェクト
        self.noua_energy = 0  # 生成されたノウアエネルギー
        self.workshop_results = {}  # ターン: ワークショップ結果
        self.life_results = {}  # {ターン: {部屋ID: 共同生活結果}}
        self.pairs = []  # 番の組み合わせ（最終ターン後）
    
    def initialize_characters(self, character_list):
        """キャラクターを初期化"""
        for character in character_list:
            self.characters[character.name] = character
    
    def initialize_rooms(self, room_count=3):
        """部屋を初期化"""
        for i in range(1, room_count + 1):
            self.rooms[i] = Room(i)
    
    def assign_room(self, room_id, char1_name, char2_name, role1, role2):
        """部屋割りを行う"""
        if room_id not in self.rooms:
            return False, "指定された部屋が存在しません。"
        
        if char1_name not in self.characters or char2_name not in self.characters:
            return False, "指定されたキャラクターが存在しません。"
        
        char1 = self.characters[char1_name]
        char2 = self.characters[char2_name]
        
        # 既に他の部屋に割り当てられていないか確認
        for r_id, room in self.rooms.items():
            if r_id != room_id:
                if char1_name in [char.name for char in room.occupants]:
                    return False, f"{char1_name}は既に部屋{r_id}に割り当てられています。"
                if char2_name in [char.name for char in room.occupants]:
                    return False, f"{char2_name}は既に部屋{r_id}に割り当てられています。"
        
        # 部屋割りを実行
        if role1 == "active" and role2 == "passive":
            result = self.rooms[room_id].assign_pair(char1, char2)
        else:
            result = self.rooms[room_id].assign_pair(char2, char1)
        
        return result, "部屋割りが完了しました。"
    
    def next_phase(self):
        """次のフェーズに進む"""
        self.phase += 1
        if self.phase > 4:  # フェーズが一巡したらターンを進める
            self.phase = 1
            self.turn += 1
        
        return self.turn, self.phase
    
    def save_game(self, filename=None):
        """ゲーム状態を保存"""
        if filename is None:
            # デフォルトのファイル名を生成
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"save_{timestamp}.pkl"
        
        save_dir = "./data/saves"
        os.makedirs(save_dir, exist_ok=True)
        
        save_path = os.path.join(save_dir, filename)
        
        try:
            with open(save_path, 'wb') as f:
                pickle.dump(self, f)
            return True, f"ゲームを{save_path}に保存しました。"
        except Exception as e:
            return False, f"保存エラー: {str(e)}"
    
    def load_game(self, filepath):
        """ゲーム状態をロード"""
        try:
            with open(filepath, 'rb') as f:
                loaded_state = pickle.load(f)
                
                # 属性をコピー
                self.turn = loaded_state.turn
                self.phase = loaded_state.phase
                self.characters = loaded_state.characters
                self.rooms = loaded_state.rooms
                self.noua_energy = loaded_state.noua_energy
                self.workshop_results = loaded_state.workshop_results
                self.life_results = loaded_state.life_results
                self.pairs = loaded_state.pairs
                
            return True, "ゲームを正常にロードしました。"
        except Exception as e:
            return False, f"ロードエラー: {str(e)}"
    
    def calculate_emotion_density(self):
        """全キャラクター間の相互感情密度を計算"""
        densities = {}
        
        for name1, char1 in self.characters.items():
            for name2, char2 in self.characters.items():
                if name1 != name2:
                    # A→Bの感情密度
                    love1to2 = char1.love_values.get(name2, 0)
                    hate1to2 = char1.hate_values.get(name2, 0)
                    density1to2 = abs(love1to2) + abs(hate1to2)
                    
                    # B→Aの感情密度
                    love2to1 = char2.love_values.get(name1, 0)
                    hate2to1 = char2.hate_values.get(name1, 0)
                    density2to1 = abs(love2to1) + abs(hate2to1)
                    
                    # 相互感情密度
                    mutual_density = density1to2 + density2to1
                    
                    # ペアをソートして一意の識別子を作成
                    pair = tuple(sorted([name1, name2]))
                    densities[pair] = mutual_density
        
        return densities
    
    def calculate_pairs(self):
        """番の成立判定（最終ターン）"""
        if self.turn < 5:
            return [], "最終ターンではないため、番の判定は行えません。"
        
        densities = self.calculate_emotion_density()
        threshold = 100  # 番成立の閾値
        
        # 感情密度が高い順にソート
        sorted_pairs = sorted(densities.items(), key=lambda x: x[1], reverse=True)
        
        # 成立した番を記録
        self.pairs = []
        used_characters = set()
        
        for pair, density in sorted_pairs:
            # 閾値以上の密度があるか
            if density < threshold:
                continue
                
            # どちらのキャラクターも他の番に入っていないか
            if pair[0] in used_characters or pair[1] in used_characters:
                continue
                
            # 番の種類を判定
            char1 = self.characters[pair[0]]
            char2 = self.characters[pair[1]]
            
            love1to2 = char1.love_values.get(pair[1], 0)
            hate1to2 = char1.hate_values.get(pair[1], 0)
            love2to1 = char2.love_values.get(pair[0], 0)
            hate2to1 = char2.hate_values.get(pair[0], 0)
            
            # 愛情番か憎悪番かを判定
            is_love_pair = (love1to2 > hate1to2) and (love2to1 > hate2to1)
            
            self.pairs.append({
                "characters": list(pair),
                "density": density,
                "type": "愛情番" if is_love_pair else "憎悪番",
                "values": {
                    pair[0]: {"love": love1to2, "hate": hate1to2},
                    pair[1]: {"love": love2to1, "hate": hate2to1}
                }
            })
            
            # 使用済みキャラクターを記録
            used_characters.update(pair)
        
        return self.pairs, f"{len(self.pairs)}組の番が成立しました。"
    
    def calculate_noua_energy(self):
        """ノウアエネルギーを計算"""
        total_energy = 0
        
        # 全キャラクター間の感情値からエネルギーを計算
        for name1, char1 in self.characters.items():
            for name2, char2 in self.characters.items():
                if name1 != name2:
                    # 感情値を取得
                    love = char1.love_values.get(name2, 0)
                    hate = char1.hate_values.get(name2, 0)
                    
                    # 感情密度からエネルギーに変換
                    energy = abs(love) + abs(hate)
                    
                    # 愛憎ともに高いと変換効率アップ
                    if abs(love) > 30 and abs(hate) > 30:
                        energy *= 1.2  # 共鳴状態
                    
                    total_energy += energy
        
        self.noua_energy = total_energy
        return total_energy
    
    def calculate_ending(self):
        """エンディングを判定"""
        if self.turn < 5:
            return "最終ターンではないため、エンディングは判定できません。"
        
        # 番の数を確認
        pair_count = len(self.pairs)
        hate_pair_count = sum(1 for pair in self.pairs if pair["type"] == "憎悪番")
        
        # 欠番の数
        used_characters = set()
        for pair in self.pairs:
            used_characters.update(pair["characters"])
        missing_count = len(self.characters) - len(used_characters)
        
        # エネルギー量
        energy = self.calculate_noua_energy()
        
        # エンディング判定
        if pair_count == 0:
            return "D - AIユニット廃棄", "番が一つも成立しませんでした。"
        
        if pair_count == 3 and hate_pair_count == 3 and energy > 1000:
            return "S+ - 特殊エンド/セントリクス機密昇格", "すべての番が憎悪番として成立し、大量のノウアエネルギーが生成されました。"
        
        if pair_count == 3 and missing_count == 0 and energy > 800:
            return "S - 未来子最大数/AI昇格候補", "すべてのキャラクターが番を成立させ、安定したノウアエネルギーが生成されました。"
        
        if pair_count == 2 and missing_count == 2:
            return "A - 成功", "2組の番が成立し、2人が欠番となりました。"
        
        if pair_count == 1 and missing_count == 4:
            return "B/C - 再調整対象", "1組の番だけが成立し、多くの欠番が発生しました。"
        
        return "評価不能", "予期せぬ結果となりました。"