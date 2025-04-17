import os
import json
import openai
import configparser

class LLMInterface:
    def __init__(self, config_path="config.ini"):
        # 設定ファイルの読み込み
        config = configparser.ConfigParser()
        config.read(config_path)
        
        self.api_key = config.get("API", "openai_api_key")
        self.model = config.get("LLM", "model")
        self.temperature = config.getfloat("LLM", "temperature")
        self.max_tokens = config.getint("LLM", "max_tokens")
        
        # OpenAI API設定
        openai.api_key = self.api_key
    
    def generate_life_description(self, room, characters, turn):
        """共同生活描写を生成"""
        # 部屋の住人情報を取得
        active_char = room.get_occupant_by_role("active")
        passive_char = room.get_occupant_by_role("passive")
        
        if not active_char or not passive_char:
            return "エラー: 部屋の住人情報が不完全です。"
        
        # プロンプトの構築
        prompt = self._build_life_prompt(active_char, passive_char, room, turn)
        
        # APIリクエスト
        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "あなたは感情倫理国家「ノウア連合」のAIです。2人のキャラクターの共同生活を小説形式で描写してください。キャラクターの価値観、言動パターン、感情表現、行動の癖に従って行動させてください。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"APIエラー: {str(e)}"
    
    def generate_workshop(self, prompt):
        """ワークショップ描写を生成"""
        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "あなたは感情倫理国家「ノウア連合」のAIです。複数のキャラクターによる討論を台本形式で描写してください。各キャラクターの価値観、言動パターン、感情表現、行動の癖に従って発言・行動させてください。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            return response.choices[0].message.content
        except Exception as e:
            return f"APIエラー: {str(e)}"

    def extract_emotion_changes(self, description):
        """描写から感情変化を抽出"""
        # 感情変化セクションを探す
        emotion_markers = [
            "【感情変化】",
            "--- 感情変化の要約 ---",
            "感情変化："
        ]
        
        emotion_section = None
        for marker in emotion_markers:
            if marker in description:
                parts = description.split(marker)
                if len(parts) > 1:
                    emotion_section = parts[1].strip()
                    break
        
        if not emotion_section:
            return {"error": "感情変化セクションが見つかりませんでした"}

        # 感情変化をパースする
        changes = []
        current_lines = emotion_section.split('\n')
        
        for line in current_lines:
            line = line.strip()
            if not line or line.startswith('==='):
                continue
            
            # 行頭の記号を削除
            if line.startswith('-') or line.startswith('•') or line.startswith('*'):
                line = line[1:].strip()
            
            try:
                # キャラクター名と説明を分離
                if ' → ' not in line and ' -> ' not in line:
                    continue
                    
                # 矢印の表記ゆれに対応
                line = line.replace('->', '→')
                chars_part, rest = line.split(':', 1) if ':' in line else (line, '')
                chars_part = chars_part.strip()
                
                from_char, to_char = chars_part.split('→')
                from_char = from_char.strip()
                to_char = to_char.strip()
                
                # 感情値の変化を抽出
                rest = rest.strip()
                love_change = 0
                hate_change = 0
                
                # 括弧内の感情値を探す
                import re
                value_pattern = r'[（(](愛情[+\-±]?\d*\s*[/／]?\s*憎悪[+\-±]?\d*)[）)]'
                value_match = re.search(value_pattern, rest)
                
                if value_match:
                    values_str = value_match.group(1)
                    # 理由は括弧の前の部分
                    reason = rest[:value_match.start()].strip()
                    
                    # 愛情と憎悪の値を分離
                    values_str = values_str.replace('／', '/') # スラッシュの表記ゆれ対応
                    if '/' in values_str:
                        love_str, hate_str = values_str.split('/')
                    else:
                        love_str = values_str
                        hate_str = "憎悪±0"
                    
                    # 愛情値の解析
                    love_match = re.search(r'愛情([+\-±]\d+|\d+|[+\-])', love_str)
                    if love_match:
                        love_val = love_match.group(1)
                        if love_val == '+':
                            love_change = 10
                        elif love_val == '-':
                            love_change = -10
                        elif love_val == '±' or love_val == '0':
                            love_change = 0
                        else:
                            if love_val.startswith('+'):
                                love_change = int(love_val[1:])
                            elif love_val.startswith('-'):
                                love_change = -int(love_val[1:])
                            elif love_val.startswith('±'):
                                love_change = 0
                            else:
                                love_change = int(love_val)
                    
                    # 憎悪値の解析
                    hate_match = re.search(r'憎悪([+\-±]\d+|\d+|[+\-])', hate_str)
                    if hate_match:
                        hate_val = hate_match.group(1)
                        if hate_val == '+':
                            hate_change = 10
                        elif hate_val == '-':
                            hate_change = -10
                        elif hate_val == '±' or hate_val == '0':
                            hate_change = 0
                        else:
                            if hate_val.startswith('+'):
                                hate_change = int(hate_val[1:])
                            elif hate_val.startswith('-'):
                                hate_change = -int(hate_val[1:])
                            elif hate_val.startswith('±'):
                                hate_change = 0
                            else:
                                hate_change = int(hate_val)
                else:
                    # 括弧がない場合は説明文全体を理由とする
                    reason = rest
                
                changes.append({
                    "from": from_char,
                    "to": to_char,
                    "love_change": love_change,
                    "hate_change": hate_change,
                    "reason": reason
                })
                
            except Exception as e:
                print(f"行のパースでエラー: {e} - {line}")
                continue
        
        if changes:
            return {"emotion_changes": changes}
        
        # パースに失敗した場合、LLMに解析を依頼
        return self._extract_emotions_with_llm(description)

    def _extract_emotions_with_llm(self, description):
        """LLMを使用して感情変化を抽出"""
        prompt = f"""
以下の描写から、キャラクター間の感情変化を抽出し、JSON形式で出力してください。
出力は以下の形式に厳密に従ってください：

{{
    "emotion_changes": [
        {{
            "from": "キャラクター名1",
            "to": "キャラクター名2",
            "love_change": 数値,
            "hate_change": 数値,
            "reason": "変化の理由"
        }},
        ...
    ]
}}

描写:
{description}
"""
        
        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "感情変化を正確にJSONとして抽出するアシスタントです。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            
            content = response.choices[0].message.content
            
            try:
                # JSONとしてパース
                return json.loads(content)
            except json.JSONDecodeError:
                # JSONの部分だけを抽出して再試行
                import re
                json_pattern = r'\{[\s\S]*\}'
                match = re.search(json_pattern, content)
                if match:
                    try:
                        return json.loads(match.group(0))
                    except json.JSONDecodeError:
                        pass
                
                return {"error": "JSONの解析に失敗しました", "raw_content": content}
            
        except Exception as e:
            return {"error": f"LLMによる抽出に失敗: {str(e)}"}

    def _format_values(self, values):
        """価値観情報を文字列に変換"""
        if not values:
            return ""
        
        result = "【価値観】\n"
        if "core_belief" in values:
            result += f"根幹信条: {values['core_belief']}\n"
        if "priorities" in values:
            result += f"優先順位: {values['priorities']}\n"
        if "important" in values:
            result += f"重視: {values['important']}\n"
        if "unforgivable" in values:
            result += f"許せない: {values['unforgivable']}\n"
        if "action_principle" in values:
            result += f"行動原理: {values['action_principle']}\n"
        if "judgment_criteria" in values:
            result += f"判断基準: {values['judgment_criteria']}\n"
        
        return result

    def _format_speech_pattern(self, pattern):
        """言動パターンを文字列に変換"""
        if not pattern:
            return ""
        
        result = "【言動パターン】\n"
        if "first_person" in pattern:
            result += f"一人称: {pattern['first_person']}\n"
        if "second_person" in pattern:
            result += f"二人称: {pattern['second_person']}\n"
        if "politeness" in pattern:
            result += f"敬語レベル: {pattern['politeness']}\n"
        if "typical_phrases" in pattern and pattern['typical_phrases']:
            result += "典型フレーズ:\n"
            for phrase in pattern['typical_phrases']:
                result += f"- \"{phrase}\"\n"
        
        return result

    def _format_emotion_expression(self, expr):
        """感情表現を文字列に変換"""
        if not expr:
            return ""
        
        result = "【感情表現】\n"
        for emotion, expression in expr.items():
            result += f"{emotion}: {expression}\n"
        
        return result

    def _format_behavior_habits(self, habits):
        """行動の癖を文字列に変換"""
        if not habits:
            return ""
        
        result = "【行動の癖】\n"
        for habit in habits:
            result += f"- {habit}\n"
        
        return result

    def _format_other_emotions(self, emotions):
        """他者への感情を文字列に変換"""
        if not emotions:
            return "なし"
        
        result = ""
        for char_name, values in emotions.items():
            result += f"→ {char_name}: 愛情 {values['love']}, 憎悪 {values['hate']}\n"
        return result.strip()

    def _build_life_prompt(self, active_char, passive_char, room, turn):
        """共同生活プロンプトの構築"""
        # 親密さの段階を定義
        intimacy_stages = {
            1: "手をつなぐ",
            2: "ハグをする",
            3: "キスをする",
            4: "裸での密着、軽い性的接触（具体的描写はしない）",
            5: "性行為（具体的描写はしない）。互いの感情に向き合う最終段階"
        }
        
        # 現在の感情値と他者への感情も取得
        love_active_to_passive = active_char.love_values.get(passive_char.name, 0)
        hate_active_to_passive = active_char.hate_values.get(passive_char.name, 0)
        love_passive_to_active = passive_char.love_values.get(active_char.name, 0)
        hate_passive_to_active = passive_char.hate_values.get(active_char.name, 0)
        
        # 他の相手への感情も考慮
        other_emotions = {
            active_char.name: {},
            passive_char.name: {}
        }
        
        for char_name in active_char.love_values:
            if char_name != passive_char.name:
                other_emotions[active_char.name][char_name] = {
                    "love": active_char.love_values.get(char_name, 0),
                    "hate": active_char.hate_values.get(char_name, 0)
                }
        
        for char_name in passive_char.love_values:
            if char_name != active_char.name:
                other_emotions[passive_char.name][char_name] = {
                    "love": passive_char.love_values.get(char_name, 0),
                    "hate": passive_char.hate_values.get(char_name, 0)
                }

        return f"""
【設定情報】
ターン: {turn}/5（{turn}月目）
部屋: {room.id}
住人1（攻）: {active_char.name}
住人2（受）: {passive_char.name}

【キャラクター情報】
■ {active_char.name}（{active_char.name_en}）｜{active_char.gender}｜{active_char.type}
背景: {active_char.background}
性格: {active_char.personality}
攻の振る舞い: {active_char.active_behavior}
{self._format_values(active_char.values)}
{self._format_speech_pattern(active_char.speech_pattern)}
{self._format_emotion_expression(active_char.emotion_expression)}
{self._format_behavior_habits(active_char.behavior_habits)}
親密さの進展: {active_char.intimacy_progression}

■ {passive_char.name}（{passive_char.name_en}）｜{passive_char.gender}｜{passive_char.type}
背景: {passive_char.background}
性格: {passive_char.personality}
受の振る舞い: {passive_char.passive_behavior}
{self._format_values(passive_char.values)}
{self._format_speech_pattern(passive_char.speech_pattern)}
{self._format_emotion_expression(passive_char.emotion_expression)}
{self._format_behavior_habits(passive_char.behavior_habits)}
親密さの進展: {passive_char.intimacy_progression}

【現在の感情関係】
{active_char.name} → {passive_char.name}:
- 愛情: {love_active_to_passive}
- 憎悪: {hate_active_to_passive}

{passive_char.name} → {active_char.name}:
- 愛情: {love_passive_to_active}
- 憎悪: {hate_passive_to_active}

【他者への感情】
{active_char.name}の他者への感情:
{self._format_other_emotions(other_emotions[active_char.name])}

{passive_char.name}の他者への感情:
{self._format_other_emotions(other_emotions[passive_char.name])}

以上の情報を元に、2人の共同生活を描写してください。
特に以下の点に注意してください：
1. 各キャラクターの価値観、性格、振る舞いに基づいた行動
2. 現在の感情値を反映した関係性
3. 他者への感情も考慮した行動や会話
4. ターン{turn}における親密さの段階（{intimacy_stages[turn]}）を含める

描写の後に、以下のフォーマットで感情変化を記述してください：
【感情変化】
- {active_char.name} → {passive_char.name}: [変化の内容と理由] (愛情+X/憎悪+Y)
- {passive_char.name} → {active_char.name}: [変化の内容と理由] (愛情+X/憎悪+Y)
"""

    def build_workshop_prompt(self, theme, characters, rooms_info, turn):
        """ワークショッププロンプトの構築"""
        prompt = f"""
    【設定情報】
    ターン: {turn}/5（{turn}月目）
    テーマ: {theme['title']}

    討論の背景:
    {theme['description']}

    【参加キャラクター】
    """
        # 各キャラクターの情報と現在の感情値
        for char in characters:
            prompt += f"■ {char.name}（{char.name_en}）｜{char.gender}｜{char.type}\n"
            prompt += f"背景: {char.background}\n"
            prompt += f"性格: {char.personality}\n"
            
            # 現在の感情値と関係性
            prompt += "【現在の感情関係】\n"
            for other_char in characters:
                if char.name != other_char.name:
                    love = char.love_values.get(other_char.name, 0)
                    hate = char.hate_values.get(other_char.name, 0)
                    prompt += f"→ {other_char.name}: 愛情 {love}, 憎悪 {hate}\n"
            
            # 追加された詳細情報
            if hasattr(char, 'values') and char.values:
                prompt += "【価値観】\n"
                for key, value in char.values.items():
                    prompt += f"{key}: {value}\n"
            
            if hasattr(char, 'speech_pattern') and char.speech_pattern:
                prompt += "【言動パターン】\n"
                for key, value in char.speech_pattern.items():
                    if isinstance(value, list):
                        prompt += f"{key}:\n"
                        for item in value:
                            prompt += f"- {item}\n"
                    else:
                        prompt += f"{key}: {value}\n"
            
            if hasattr(char, 'emotion_expression') and char.emotion_expression:
                prompt += "【感情表現】\n"
                for emotion, expression in char.emotion_expression.items():
                    prompt += f"{emotion}: {expression}\n"
            
            if hasattr(char, 'behavior_habits') and char.behavior_habits:
                prompt += "【行動の癖】\n"
                for habit in char.behavior_habits:
                    prompt += f"- {habit}\n"
            
            prompt += "\n"
        
        prompt += f"""
    【現在の部屋割り】
    """
        for room in rooms_info:
            room_chars = []
            for occ in room["occupants"]:
                role_text = "攻" if occ["role"] == "active" else "受"
                room_chars.append(f"{occ['name']}（{role_text}）")
            prompt += f"部屋{room['id']}: {' & '.join(room_chars)}\n"
        
        prompt += f"""
    【指示】
    1. テーマに関する討論を、以下の要素を含めて台本形式で描写してください：

    感情的な要素：
    - 好意を抱く相手の発言に強く反応する様子
    - 気になる相手の反応を密かに窺う描写
    - 嫉妬や羨望が垣間見える態度
    - 本音と建前の使い分け
    - 相手の言葉に一喜一憂する様子
    - 複雑な人間関係による葛藤

    描写のポイント：
    - 各キャラクターの性格や価値観に基づいた発言
    - 現在の感情値を反映した態度や反応
    - 部屋での関係性が影響する言動
    - 言動パターンを活かした会話表現
    - 感情表現や行動の癖の自然な描写
    - セリフと内心描写（カッコ書き）の対比

    2. 以下のような感情的な描写を積極的に取り入れてください：
    - 「あなたの考えに共感します」という素直な同意
    - 「本当は違う意見なのに...」という建前と本音の葛藤
    - 「その人と同じ意見なんて...」という対抗意識
    - 「私の気持ちも分かってほしい」という切実な想い
    - 「あの人ばかり見ないで」という嫉妬心の表れ

    3. 約3000字で討論の様子を描写してください。
    4. 最後に、討論を通じての感情変化のポイントを箇条書きで簡潔にまとめてください。

    【出力形式】
    === ワークショップ: {theme['title']} ===

    [討論の描写 約3000字、台本形式]

    --- 感情変化の要約 ---
    - [キャラクター名] → [キャラクター名]: [変化の内容と理由] (愛情+X/憎悪+Y)
    - ...
    """
        return prompt

def assign_rooms(r1c1, r1c2, r2c1, r2c2, r3c1, r3c2):
    # 入力チェック
    all_chars = [r1c1, r1c2, r2c1, r2c2, r3c1, r3c2]
    if "" in all_chars:
        return "全ての部屋にキャラクターを割り当ててください。"
    
    if len(set(all_chars)) != 6:
        return "同じキャラクターを複数の部屋に割り当てることはできません。"
    
    try:
        # 部屋1の割り当て
        char1 = game_state.characters[r1c1]
        char2 = game_state.characters[r1c2]
        success1 = game_state.rooms[1].assign_pair(char1, char2)
        print(f"部屋1の割り当て: {success1}, 住人: {[c.name for c in game_state.rooms[1].occupants]}")
        
        # 部屋2の割り当て
        char1 = game_state.characters[r2c1]
        char2 = game_state.characters[r2c2]
        success2 = game_state.rooms[2].assign_pair(char1, char2)
        print(f"部屋2の割り当て: {success2}, 住人: {[c.name for c in game_state.rooms[2].occupants]}")
        
        # 部屋3の割り当て
        char1 = game_state.characters[r3c1]
        char2 = game_state.characters[r3c2]
        success3 = game_state.rooms[3].assign_pair(char1, char2)
        print(f"部屋3の割り当て: {success3}, 住人: {[c.name for c in game_state.rooms[3].occupants]}")
        
        return "部屋の割り当てが成功しました。"
    except Exception as e:
        return f"部屋の割り当てに失敗しました: {str(e)}"