import os
import json
import configparser
import gradio as gr
from modules.character import Character
from modules.room import Room
from modules.game_state import GameState
from modules.llm_interface import LLMInterface
import pandas as pd

# 設定読み込み
def load_config():
    config = configparser.ConfigParser()
    if not os.path.exists("config.ini"):
        # 設定ファイルがなければデフォルト作成
        config["API"] = {
            "openai_api_key": "あなたのAPIキーをここに入力"
        }
        config["GAME"] = {
            "debug_mode": "True",
            "save_directory": "./data/saves"
        }
        config["LLM"] = {
            "model": "gpt-4.1-2025-04-14",
            "temperature": "0.7",
            "max_tokens": "4000"
        }
        
        # 設定ファイル保存
        os.makedirs("./data", exist_ok=True)
        with open("config.ini", "w") as f:
            config.write(f)
    else:
        config.read("config.ini")
    
    return config

# キャラクターデータ読み込み
def load_characters():
    # データディレクトリ確認
    os.makedirs("./data", exist_ok=True)
    
    characters_file = "./data/characters.json"
    
    # ファイルが存在しなければサンプルデータ作成
    if not os.path.exists(characters_file):
        create_sample_characters()
    
    # ファイル読み込み
    with open(characters_file, "r", encoding="utf-8") as f:
        char_data = json.load(f)
    
    characters = []
    characters_data = create_sample_characters()
    
    for name, data in characters_data.items():
        # データに名前を追加
        data["name"] = name
        # Characterオブジェクトを作成
        character = Character(data)
        characters.append(character)
    
    return characters

# サンプルキャラクターデータ作成
def create_sample_characters():
    characters_data = {
        "ルミナ": {
            "name_en": "Lumina Korr",
            "gender": "F",
            "type": "感情吸収型（愛情共鳴）",
            "background": "幼少期から他者の感情に敏感で、共感しすぎて体調を崩すことも。独りで空想を楽しみ、日記に言葉を綴る。セロへの想いとネラの執着に揺れ、番制度への楽観が崩れつつある。",
            "personality": "静かで繊細、他人の感情に強く反応。対立を避けるが、裏切りに傷つきやすくなった。",
            "initial_emotions": {
                "love": {
                    "シルフィ": {
                        "value": 20,
                        "reason": "情熱と自由な表現に心を奪われ、憧れている"
                    },
                    "セロ": {
                        "value": 35,
                        "reason": "明るさと優しさに強く惹かれるが、ネラの影に不安"
                    },
                    "ネラ": {
                        "value": 5,
                        "reason": "かつて親しみを感じたが、セロへの執着に恐怖"
                    },
                    "カイル": {
                        "value": 40,
                        "reason": "穏やかな支えに心を許すが、隠された意図に疑念"
                    },
                    "オーギュスト": {
                        "value": -20,
                        "reason": "感情を否定する冷酷さに強い反発と恐怖"
                    }
                },
                "hate": {
                    "シルフィ": {
                        "value": 5,
                        "reason": "セロへの親密さに嫉妬、情熱に圧倒される"
                    },
                    "セロ": {
                        "value": 0,
                        "reason": "軽率さに戸惑うが、憎しみには至らない"
                    },
                    "ネラ": {
                        "value": 10,
                        "reason": "セロへの病的執着と敵意に強い不信と恐怖"
                    },
                    "カイル": {
                        "value": 15,
                        "reason": "優しさの裏に隠された策略に警戒心"
                    },
                    "オーギュスト": {
                        "value": 25,
                        "reason": "感情を数値化する姿勢に深い嫌悪と恐怖"
                    }
                }
            },
            "active_behavior": "控えめにアプローチ、信頼を求める。裏切られると感情的な訴えに走る。例: 「……セロ、わたしを信じてくれるよね？」",
            "passive_behavior": "共感があれば応じるが、裏切りや強引さに憎悪急増。例: 「……そんな言葉、傷つくだけだよ。」",
            "values": {
                "core_belief": "わたしの心は本当の絆を映す。でも裏切りは許せない",
                "priorities": "信頼と共感 > 心の安全 > 自己防衛",
                "important": "本音の共有、裏切りのない関係、心の安らぎ",
                "unforgivable": "裏切り、感情の軽視、意図的な傷つけ",
                "action_principle": "本心を見極め、心を慎重に開く",
                "judgment_criteria": "「この人はわたしを裏切らないか」"
            },
            "speech_pattern": {
                "first_person": "わたし",
                "second_person": "あなた、○○くん／○○ちゃん",
                "politeness": "丁寧、感情が高ぶると率直",
                "typical_phrases": [
                    "……ううん、ただ怖いだけ",
                    "お願い、わたしを裏切らないで",
                    "どうしてそんな目で見るの……？"
                ]
            },
            "emotion_expression": {
                "surprise": "瞳を見開き震える、「え……どういうこと？」",
                "anger": "涙をこらえ声を震わせる、「ひどいよ……許せない」",
                "joy": "頬を赤らめ微笑む、「こんな気持ち、初めてだよ……」",
                "anxiety": "袖を強く握り視線を泳がせる、「信じていいよね？」"
            },
            "behavior_habits": [
                "不安時に日記のページをめくる",
                "感情が高ぶると指先を震わせる",
                "誰かの視線を感じると肩をすくめる"
            ],
            "intimacy_progression": "推奨段階を慎重に進める。信頼の裏切りや強引な攻に憎悪急増（+20）。セロやカイルとの親密さは急速に進む可能性。"
        },
        "セロ": {
            "name_en": "Cero Vann",
            "gender": "M",
            "type": "社交扇動型（空気攪拌）",
            "background": "明るく活発、誰とでも話せる才能。無意識に感情をかき乱す。ネラとの幼少期の約束（「ずっとそばにいる」）を忘れ、彼女の執着に戸惑う。",
            "personality": "陽気で人懐っこい。責任感が薄く、深刻な感情に逃げ腰。",
            "initial_emotions": {
                "love": {
                    "シルフィ": {
                        "value": 25,
                        "reason": "情熱と自由な魂に強く惹かれ、共に高揚する"
                    },
                    "ルミナ": {
                        "value": 40,
                        "reason": "純粋な感情に心を動かされ、守りたい衝動"
                    },
                    "ネラ": {
                        "value": 10,
                        "reason": "懐かしさを感じるが、執着に強い戸惑い"
                    },
                    "カイル": {
                        "value": 0,
                        "reason": "穏やかさに好感はあるが、裏の意図に警戒"
                    },
                    "オーギュスト": {
                        "value": -15,
                        "reason": "冷淡さに苦手意識、支配的な態度に反発"
                    }
                },
                "hate": {
                    "シルフィ": {
                        "value": 5,
                        "reason": "情熱が時に過剰で振り回される感覚"
                    },
                    "ルミナ": {
                        "value": 0,
                        "reason": "感情的な反応に戸惑うが、憎しみはない"
                    },
                    "ネラ": {
                        "value": 15,
                        "reason": "病的執着と重い圧力に強い居心地の悪さ"
                    },
                    "カイル": {
                        "value": 20,
                        "reason": "ルミナへの暗躍と牽制に強い不信"
                    },
                    "オーギュスト": {
                        "value": 25,
                        "reason": "冷淡さに苦手意識、支配的な態度に反発"
                    }
                }
            },
            "active_behavior": "軽快にスキンシップで接近、無自覚に周囲を振り回す。例: 「よっ、ルミナ、ハグでノリ上げようぜ！」",
            "passive_behavior": "気軽に応じるが、執着や重い感情に逃げる。例: 「ネラ、ちょっと重いって、落ち着こう？」",
            "values": {
                "core_belief": "楽しく生きるのが一番、深刻なのは苦手",
                "priorities": "快楽とノリ > 軽い関係 > 責任回避",
                "important": "笑顔、自由な雰囲気、気軽なつながり",
                "unforgivable": "重い執着、場の空気を壊す行為",
                "action_principle": "楽しい流れに乗り、深刻さは避ける",
                "judgment_criteria": "「この瞬間、楽しめるか」"
            },
            "speech_pattern": {
                "first_person": "オレ",
                "second_person": "お前、キミ、○○ちゃん",
                "politeness": "タメ口、軽薄で親しげ",
                "typical_phrases": [
                    "マジ？ それめっちゃウケる！",
                    "おっと、ネラ、ちょっと重いぜ？",
                    "いいじゃん、ノリでいこうぜ！"
                ]
            },
            "emotion_expression": {
                "surprise": "「マジかよ！ ウソだろ！？」と大声で手を広げる",
                "anger": "冗談っぽく声を荒げる、「おい、なにそれ、ムカつくんだけど？」",
                "joy": "肩を叩き笑う、「サイコー！ お前、最高だな！」",
                "anxiety": "軽く笑ってごまかす、「まぁ、なんとかなるっしょ？」"
            },
            "behavior_habits": [
                "無意識に相手の肩に手を置く",
                "緊張時に足でリズムを刻む",
                "深刻な話を冗談で流す"
            ],
            "intimacy_progression": "推奨段階を軽快に進めるが、ネラの執着に憎悪急増（+15）。シルフィやルミナとの親密さは急速に進む可能性。"
        },
        "ネラ": {
            "name_en": "Nella Krynn",
            "gender": "F",
            "type": "片想い執着型（感情偏重）",
            "background": "感情表現が乏しく、観察に徹する。セロとの幼少期の約束（「ずっとそばにいる」）を心の支えにし、病的執着を抱く。ルミナやシルフィをライバル視し、番制度に深い不信感。",
            "personality": "無口で内面は情念の塊。セロへの独占欲が強く、敵対者を冷たく排除。",
            "initial_emotions": {
                "love": {
                    "シルフィ": {
                        "value": -5,
                        "reason": "セロへの接近と情熱に強い嫉妬"
                    },
                    "ルミナ": {
                        "value": -10,
                        "reason": "セロを奪う存在、感情的な弱さに苛立ち"
                    },
                    "セロ": {
                        "value": 95,
                        "reason": "幼少期の約束を信じ、彼だけが心の救い"
                    },
                    "カイル": {
                        "value": 0,
                        "reason": "穏やかさに興味はあるが、セロへの妨害に警戒"
                    },
                    "オーギュスト": {
                        "value": -15,
                        "reason": "支配的な態度に強い不安と嫌悪"
                    }
                },
                "hate": {
                    "シルフィ": {
                        "value": 25,
                        "reason": "セロへの親密さと自由な態度に強い敵意"
                    },
                    "ルミナ": {
                        "value": 30,
                        "reason": "セロを奪う最大の障害、純粋さに軽蔑"
                    },
                    "セロ": {
                        "value": 0,
                        "reason": "愛情が強すぎて憎しみに至らないが、裏切りに敏感"
                    },
                    "カイル": {
                        "value": 15,
                        "reason": "ルミナへの暗躍に不信、セロへの妨害に敵意"
                    },
                    "オーギュスト": {
                        "value": 20,
                        "reason": "感情を否定する姿勢に強い反発"
                    }
                }
            },
            "active_behavior": "セロに執着し、重い視線や告白で迫る。例: 「セロ、約束したよね。私だけでいいよね？」",
            "passive_behavior": "セロ以外に冷淡、敵意を隠さない。例: 「……ルミナ、近づかないで。」",
            "values": {
                "core_belief": "セロだけが私の全て、邪魔者は許さない",
                "priorities": "セロの心 > 独占欲 > ライバルの排除",
                "important": "セロへの忠誠、完全な所有、障害の排除",
                "unforgivable": "セロの裏切り、ライバルの存在、軽視",
                "action_principle": "セロを縛り、ライバルを遠ざける",
                "judgment_criteria": "「セロは私だけを選ぶか」"
            },
            "speech_pattern": {
                "first_person": "わたし",
                "second_person": "○○、あなた（敬称なし）",
                "politeness": "無感情で鋭い、セロには切実",
                "typical_phrases": [
                    "セロ、私だけでいいよね……",
                    "ルミナ、なぜあなたが彼のそばに……？",
                    "約束を、忘れないで……"
                ]
            },
            "emotion_expression": {
                "surprise": "目を見開き固まる、「……何？」",
                "anger": "無表情で鋭い視線、「許さない……」",
                "joy": "セロをじっと見つめ微笑む、「やっと、そばにいてくれる」",
                "anxiety": "爪を噛み服を握る、「セロ、行かないで……」"
            },
            "behavior_habits": [
                "セロの近くで無言で観察",
                "ルミナやシルフィに冷たい視線",
                "不安時に爪を強く噛む"
            ],
            "intimacy_progression": "セロに全力を注ぎ、推奨段階を無視して迫る。ルミナやシルフィへの憎悪が急増（+15/ターン）。他者には無関心。"
        },
        "オーギュスト": {
            "name_en": "Auguste Thale",
            "gender": "M",
            "type": "理性傲慢型（支配者気質）",
            "background": "頭脳明晰、感情を無駄とみなす。シルフィの情熱に理性では抗えない魅力を感じ、自己嫌悪に苛まれる。番制度は効率の最適化とみなす。",
            "personality": "冷静で支配的。シルフィへの執着を隠し、他人をコントロールする。",
            "initial_emotions": {
                "love": {
                    "ルミナ": {
                        "value": -20,
                        "reason": "感情的な弱さがシステムの効率を下げる"
                    },
                    "セロ": {
                        "value": -15,
                        "reason": "軽率さに強い苛立ち"
                    },
                    "ネラ": {
                        "value": 5,
                        "reason": "執着の一貫性に一定の評価"
                    },
                    "シルフィ": {
                        "value": 25,
                        "reason": "情熱と歌声に理性では抗えない強い魅力"
                    },
                    "カイル": {
                        "value": 15,
                        "reason": "論理的思考に共感、信頼の可能性"
                    }
                },
                "hate": {
                    "ルミナ": {
                        "value": 25,
                        "reason": "感情優先の行動がシステムを乱す"
                    },
                    "セロ": {
                        "value": 20,
                        "reason": "無責任な態度に強い不信"
                    },
                    "ネラ": {
                        "value": 5,
                        "reason": "執着が非効率的と感じる瞬間"
                    },
                    "シルフィ": {
                        "value": 15,
                        "reason": "自身の感情を乱す存在への自己嫌悪"
                    },
                    "カイル": {
                        "value": 0,
                        "reason": "論理的な姿勢に好感"
                    }
                }
            },
            "active_behavior": "効率を装いシルフィに強引に接近。例: 「シルフィ、君の情熱は最適化に必要だ。ハグを試すべきだ。」",
            "passive_behavior": "感情的な接近を冷たく評価。例: 「その程度の熱意では無意味だ。」",
            "values": {
                "core_belief": "世界は数式、感情は制御可能な変数",
                "priorities": "効率と支配 > 秩序 > シルフィの理解",
                "important": "論理、一貫性、シルフィの情熱の解明",
                "unforgivable": "非合理な行動、感情の暴走、自身の弱さ",
                "action_principle": "全てを計算し、シルフィを理解・支配する",
                "judgment_criteria": "「これは最適な結果を生むか」"
            },
            "speech_pattern": {
                "first_person": "僕",
                "second_person": "君、○○くん／○○さん",
                "politeness": "敬語に皮肉を混ぜる",
                "typical_phrases": [
                    "無駄だ。もっと合理的な方法がある",
                    "シルフィ、君の情熱は興味深いが、制御が必要だ",
                    "感情は単なる変数、計算すべきだ"
                ]
            },
            "emotion_expression": {
                "surprise": "顎に手を当て、「……予想外だ」",
                "anger": "声を低く、「その選択は失望だ」",
                "joy": "冷たく笑う、「面白い、実に興味深い」",
                "anxiety": "無言でノートに線を引く"
            },
            "behavior_habits": [
                "シルフィを見ると無意識に瞬きが減る",
                "感情が揺れると数式を書き殴る",
                "セロに冷ややかな視線"
            ],
            "intimacy_progression": "推奨段階を無視し、シルフィに強引に迫る。拒絶で憎悪急増（+20）。セロとの過去露見で感情不安定。"
        },
        "シルフィ": {
            "name_en": "Sylphy Ardra",
            "gender": "F",
            "type": "感情乱流型（起爆因子）",
            "background": "感情の起伏が激しく、制御困難とされた過去。番制度に反感を抱き、自由と情熱を追求する芸術家肌。誰とでも仲良くできるが他者への執着はあまりしない。",
            "personality": "情熱的で衝動的。裏切りや束縛を許さず、感情を爆発させる。",
            "initial_emotions": {
                "love": {
                    "ルミナ": {
                        "value": 25,
                        "reason": "純粋さに心を動かされ、守りたいと感じる"
                    },
                    "セロ": {
                        "value": 20,
                        "reason": "軽快なノリと優しさに強い共鳴、高揚感"
                    },
                    "ネラ": {
                        "value": -15,
                        "reason": "セロへの執着と敵意に強い反発"
                    },
                    "オーギュスト": {
                        "value": 10,
                        "reason": "歌を聴く視線に複雑な魅力、支配に反発"
                    },
                    "カイル": {
                        "value": 5,
                        "reason": "穏やかさに興味はあるが、感情抑圧に距離"
                    }
                },
                "hate": {
                    "ルミナ": {
                        "value": 5,
                        "reason": "セロへの接近に嫉妬、弱さに苛立ち"
                    },
                    "セロ": {
                        "value": 0,
                        "reason": "軽率さに戸惑うが、憎しみはない"
                    },
                    "ネラ": {
                        "value": 30,
                        "reason": "セロへの病的執着に強い敵意と軽蔑"
                    },
                    "オーギュスト": {
                        "value": 20,
                        "reason": "支配的な態度と感情軽視に強い反発"
                    },
                    "カイル": {
                        "value": 15,
                        "reason": "感情を抑える姿勢と暗躍に苛立ち"
                    }
                }
            },
            "active_behavior": "感情の高ぶりで急速に接近、衝突も恐れない。例: 「セロ、ノリでキスしてみねえ？」",
            "passive_behavior": "鈍い反応や執着に激しく反発。例: 「ネラ、アンタの目はムカつくんだよ！」",
            "values": {
                "core_belief": "感情を隠す人生に価値はない",
                "priorities": "自由な表現 > 情熱 > 対等な関係",
                "important": "本音、自由、歌による共鳴",
                "unforgivable": "裏切り、束縛、感情の抑圧",
                "action_principle": "心のままに突き進む",
                "judgment_criteria": "「こいつは本気でぶつかってくるか」"
            },
            "speech_pattern": {
                "first_person": "あたし",
                "second_person": "アンタ、○○",
                "politeness": "タメ口、挑発的",
                "typical_phrases": [
                    "退屈！ アンタ、もっと本気出せよ！",
                    "ネラ、セロに近づくなら覚悟しな！",
                    "あたしの歌、感じてみねえ？"
                ]
            },
            "emotion_expression": {
                "surprise": "目を輝かせ跳ねる、「マジ！？ すげえじゃん！」",
                "anger": "声を荒げ詰め寄る、「ふざけんな、許さねえ！」",
                "joy": "抱きつき叫ぶ、「最高！ アンタ、めっちゃ好き！」",
                "anxiety": "髪を強く掴む、「やべ、しくじったかな……」"
            },
            "behavior_habits": [
                "感情が高ぶると歌い出す",
                "ネラを見ると無意識に睨む",
                "興奮時に近くの物を叩く"
            ],
            "intimacy_progression": "推奨段階を無視、セロやルミナと急速に進展。ネラの執着やオーギュストの支配に憎悪急増（+20）。"
        },
        "カイル": {
            "name_en": "Kair Elvon",
            "gender": "M",
            "type": "均衡安定型（感情制御者）",
            "background": "空気を観察し、トラブルを避ける。ノウア連合の感情収穫システムに密かな反発を抱き、ルミナをシステムから救うため暗躍。セロの軽さとネラの執着を危険視し、妨害を画策。",
            "personality": "温厚に見えるが、計算高く裏切りを隠す。ルミナへの執着が弱点。",
            "initial_emotions": {
                "love": {
                    "オーギュスト": {
                        "value": 15,
                        "reason": "論理的思考に共感、協力の可能性"
                    },
                    "ネラ": {
                        "value": 0,
                        "reason": "執着に理解を示すが、危険視"
                    },
                    "セロ": {
                        "value": -10,
                        "reason": "ルミナを惑わす軽さに強い苛立ち"
                    },
                    "シルフィ": {
                        "value": 10,
                        "reason": "情熱に興味はあるが、制御不能に警戒"
                    },
                    "ルミナ": {
                        "value": 50,
                        "reason": "純粋さに心を奪われ、システムから守りたい"
                    }
                },
                "hate": {
                    "オーギュスト": {
                        "value": 5,
                        "reason": "支配的な姿勢に潜在的な不信"
                    },
                    "ネラ": {
                        "value": 20,
                        "reason": "セロへの執着がシステムを歪め、危険"
                    },
                    "セロ": {
                        "value": 25,
                        "reason": "ルミナを振り回す無責任さに不信"
                    },
                    "シルフィ": {
                        "value": 15,
                        "reason": "感情の爆発が計画を乱す"
                    },
                    "ルミナ": {
                        "value": 0,
                        "reason": "愛情が強すぎて憎しみに至らない"
                    }
                }
            },
            "active_behavior": "穏やかにルミナを誘導、セロを巧みに牽制。例: 「ルミナ、セロの軽さは危険だよ。僕なら……」",
            "passive_behavior": "強引な接近に冷たく拒絶。例: 「シルフィ、今は無理だ、考えさせて。」",
            "values": {
                "core_belief": "システムは腐敗、ルミナだけは守る",
                "priorities": "ルミナの安全 > システムの破壊 > 自己保身",
                "important": "信頼、ルミナの心、秘密の掌握",
                "unforgivable": "ルミナへの裏切り、無責任な行動",
                "action_principle": "ルミナを救い、システムを裏切る",
                "judgment_criteria": "「ルミナを誰が守れるか」"
            },
            "speech_pattern": {
                "first_person": "僕",
                "second_person": "君、○○くん／○○さん",
                "politeness": "丁寧、裏に鋭さ",
                "typical_phrases": [
                    "ルミナ、君はもっと大切にされるべきだ",
                    "セロ、君の軽さは危険だよ",
                    "システムは、僕たちが思うほど純粋じゃない"
                ]
            },
            "emotion_expression": {
                "surprise": "眉を上げ冷静に、「……それは意外だ」",
                "anger": "静かに声を強める、「それは見過ごせない」",
                "joy": "穏やかに微笑む、「ルミナ、君は特別だ」",
                "anxiety": "目を伏せ深呼吸、「……失敗は許されない」"
            },
            "behavior_habits": [
                "ルミナを見ると無意識に微笑む",
                "セロに冷たい視線を投げる",
                "計画中は指で机を叩く"
            ],
            "intimacy_progression": "ルミナに慎重に接近、セロやネラの妨害に全力を注ぐ。暴露で憎悪急増（+20）。"
        }
    }
    
    # 保存
    os.makedirs("./data", exist_ok=True)
    with open("./data/characters.json", "w", encoding="utf-8") as f:
        json.dump(characters_data, f, ensure_ascii=False, indent=4)
    
    return characters_data

# セーブファイルの一覧を取得
def list_save_files():
    save_dir = "./data/saves"
    os.makedirs(save_dir, exist_ok=True)
    return [f for f in os.listdir(save_dir) if f.endswith(".pkl")]

# フェーズ名を取得
def phase_name(phase):
    phases = {
        1: "部屋割りフェーズ",
        2: "共同生活フェーズ",
        3: "感情ワークショップフェーズ",
        4: "感情スキャン・評価フェーズ"
    }
    return phases.get(phase, "不明なフェーズ")

# 部屋割りフェーズのUI
def room_assignment_ui(game_state):
    with gr.Column():
        gr.Markdown("## 部屋割りフェーズ")
        gr.Markdown("6人のキャラクターを3つの部屋に割り当ててください。\n※上段のキャラが攻め、下段のキャラが受けとなります。")
        
        # キャラクター一覧
        all_char_names = list(game_state.characters.keys())
        
        # 部屋割り入力フォーム
        with gr.Group():
            with gr.Accordion("部屋1", open=True):
                with gr.Row():
                    room1_char1 = gr.Dropdown(
                        label="キャラクター1（攻め）",
                        choices=[""] + all_char_names,
                        value=""
                    )
                with gr.Row():
                    room1_char2 = gr.Dropdown(
                        label="キャラクター2（受け）",
                        choices=[""] + all_char_names,
                        value=""
                    )
            
            with gr.Accordion("部屋2", open=True):
                with gr.Row():
                    room2_char1 = gr.Dropdown(
                        label="キャラクター1（攻め）",
                        choices=[""] + all_char_names,
                        value=""
                    )
                with gr.Row():
                    room2_char2 = gr.Dropdown(
                        label="キャラクター2（受け）",
                        choices=[""] + all_char_names,
                        value=""
                    )
            
            with gr.Accordion("部屋3", open=True):
                with gr.Row():
                    room3_char1 = gr.Dropdown(
                        label="キャラクター1（攻め）",
                        choices=[""] + all_char_names,
                        value=""
                    )
                with gr.Row():
                    room3_char2 = gr.Dropdown(
                        label="キャラクター2（受け）",
                        choices=[""] + all_char_names,
                        value=""
                    )
        
        # 結果表示エリア
        result_text = gr.Textbox(label="結果", interactive=False)
        
        # 割り当てボタン
        assign_btn = gr.Button("部屋を割り当て")
        
        # 選択肢を更新する関数
        def update_choices(changed_value, *current_selections):
            # 現在の選択値を取得
            selections = list(current_selections)
            
            # 選択済みのキャラクターを取得（空文字列は除外）
            selected = [s for s in selections if s]
            
            # 各ドロップダウンの選択肢と値を更新
            updated_dropdowns = []
            for i, current_value in enumerate(selections):
                if current_value:
                    # 現在選択されている値は必ず含める
                    choices = ["", current_value]
                    # 他のキャラクターで、まだ選択されていないものを追加
                    choices.extend([
                        char for char in all_char_names 
                        if char not in selected or char == current_value
                    ])
                else:
                    # 空の場合は、選択されていないキャラクターのみを表示
                    choices = [""] + [
                        char for char in all_char_names 
                        if char not in selected
                    ]
                # 重複を削除して並び替え
                choices = sorted(list(dict.fromkeys(choices)))
                updated_dropdowns.append(gr.Dropdown(choices=choices, value=current_value))
            
            return updated_dropdowns
        
        # イベントハンドラ
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
                
                if success1 and success2 and success3:
                    return "部屋の割り当てが完了しました。"
                else:
                    return "一部の部屋の割り当てに失敗しました。"
                
            except Exception as e:
                return f"エラーが発生しました: {str(e)}"
        
        # イベント関連付け
        # 各ドロップダウンの選択変更時に他のドロップダウンの選択肢を更新
        all_dropdowns = [room1_char1, room1_char2, room2_char1, room2_char2, room3_char1, room3_char2]
        
        for dropdown in all_dropdowns:
            dropdown.change(
                fn=update_choices,
                inputs=[dropdown] + all_dropdowns,
                outputs=all_dropdowns
            )
        
        # 割り当てボタンのイベント
        assign_btn.click(
            fn=assign_rooms,
            inputs=all_dropdowns,
            outputs=[result_text]
        )

# 共同生活フェーズのUI
def common_life_ui(game_state, llm_interface):
    with gr.Column():
        gr.Markdown("## 共同生活フェーズ")
        gr.Markdown("各部屋での共同生活の描写を生成します。感情変化は自動的に適用されます。")
        
        # 部屋選択
        room_select = gr.Radio(label="部屋を選択", choices=["部屋1", "部屋2", "部屋3"], value="部屋1")
        
        # 描写表示エリア
        description_area = gr.Textbox(label="共同生活の描写", lines=20)
        
        # 感情変化表示エリア
        emotion_changes = gr.Textbox(label="感情変化", lines=5)
        
        # エネルギー表示（読み取り専用）
        energy_display = gr.Textbox(label="現在のノウアエネルギー", value=str(game_state.noua_energy))
        
        # 生成ボタン
        generate_btn = gr.Button("描写を生成（感情変化も自動適用）")
        # イベントハンドラ
        def generate_description(room_name):
            room_id = int(room_name[-1])  # "部屋1" -> 1
            
            # 既に生成済みなら取得
            if game_state.turn in game_state.life_results and room_id in game_state.life_results[game_state.turn]:
                description = game_state.life_results[game_state.turn][room_id]["description"]
                emotion_text = game_state.life_results[game_state.turn][room_id].get("emotion_text", "感情変化情報がありません。")
                return description, emotion_text, str(game_state.noua_energy)
            
            # 生成
            room = game_state.rooms[room_id]
            description = llm_interface.generate_life_description(room, list(game_state.characters.values()), game_state.turn)
            
            # 結果を保存
            if game_state.turn not in game_state.life_results:
                game_state.life_results[game_state.turn] = {}
            
            # 感情変化を抽出
            emotion_result = llm_interface.extract_emotion_changes(description)
            
            # 感情変化を適用
            applied_count = 0
            if "emotion_changes" in emotion_result:
                for change in emotion_result["emotion_changes"]:
                    from_char = change["from"]
                    to_char = change["to"]
                    love_change = change["love_change"]
                    hate_change = change["hate_change"]
                    
                    if from_char in game_state.characters and to_char in game_state.characters:
                        char = game_state.characters[from_char]
                        char.update_emotion(to_char, love_change, hate_change)
                        applied_count += 1
            
            # フォーマットされた感情変化テキストを生成
            emotion_text = format_emotion_changes(emotion_result)
            if applied_count > 0:
                emotion_text += f"\n\n{applied_count}件の感情変化が自動的に適用されました。"
            
            # エネルギー再計算
            energy = game_state.calculate_noua_energy()
            game_state.noua_energy = energy
            
            # 結果を保存（適用済みフラグも含む）
            game_state.life_results[game_state.turn][room_id] = {
                "description": description,
                "emotion_changes": emotion_result,
                "emotion_text": emotion_text,
                "applied": True  # 自動適用済み
            }
            
            return description, emotion_text, str(energy)
        
        def format_emotion_changes(emotion_result):
            """感情変化データを読みやすい形式に整形"""
            if "error" in emotion_result:
                return f"感情変化の抽出エラー: {emotion_result['error']}"
            
            if "emotion_changes" not in emotion_result or not emotion_result["emotion_changes"]:
                return "感情変化を抽出できませんでした。"
            
            emotion_text = "--- 感情変化の要約 ---\n"
            for change in emotion_result["emotion_changes"]:
                from_char = change["from"]
                to_char = change["to"]
                love_change = change["love_change"]
                hate_change = change["hate_change"]
                reason = change["reason"]
                
                # 符号の処理
                love_sign = "+" if love_change > 0 else ("-" if love_change < 0 else "±")
                hate_sign = "+" if hate_change > 0 else ("-" if hate_change < 0 else "±")
                
                # 絶対値を使用し、0の場合は0と表示
                love_value = abs(love_change) if love_change != 0 else 0
                hate_value = abs(hate_change) if hate_change != 0 else 0
                
                emotion_text += f"- {from_char} → {to_char}: {reason} (愛情{love_sign}{love_value}/憎悪{hate_sign}{hate_value})\n"
            
            return emotion_text
        
        # 次のフェーズへ
        def proceed_to_next_phase():
            # 全部屋の感情変化が適用されているか確認
            all_applied = True
            if game_state.turn in game_state.life_results:
                for room_id in range(1, 4):
                    if (room_id not in game_state.life_results[game_state.turn] or 
                        not game_state.life_results[game_state.turn][room_id]["applied"]):
                        all_applied = False
                        break
            else:
                all_applied = False
            
            if not all_applied:
                return "全ての部屋の描写を生成してから次のフェーズに進んでください。", turn_text.value, phase_text.value
            
            # フェーズを進める
            turn, phase = game_state.next_phase()
            return "次のフェーズに進みました。", f"{turn}/5", phase_name(phase)
        
        # イベント関連付け
        generate_btn.click(
            fn=generate_description,
            inputs=[room_select],
            outputs=[description_area, emotion_changes, energy_display]
        )
        


# 感情ワークショップフェーズのUI
def workshop_ui(game_state, llm_interface):
    with gr.Column():
        gr.Markdown("## 感情ワークショップフェーズ")
        gr.Markdown("今月のテーマに基づいた全員参加の討論を行います。感情変化は自動的に適用されます。")
        
        # ワークショップテーマの設定
        workshop_themes = {
            1: {
                "title": "番制度はなぜ必要なのか？",
                "description": """
番になることは、個人として、そして共同体としての最適化である。
君たちはその意義をどのように理解しているだろう？
                """
            },
            2: {
                "title": "手をつなぐことの意味と効果について",
                "description": """
初期接触（手をつなぐ）は、番候補との共鳴準備に有効とされている。
君たちはどんな時に、それを選びたいと思う？
                """
            },
            3: {
                "title": "身体接触を通じた感情密度の上昇はなぜ必要か？",
                "description": """
ハグやキスといった段階的接触は、EDE理論に基づき奨励されている。
君たちはそれにどう向き合っている？
                """
            },
            4: {
                "title": "番としての適合性は、どのように見極めるべきか？",
                "description": """
感情密度の推移、身体接触時の反応、発言傾向など。
君たちは何を基準に、相手との適合を感じている？
                """
            },
            5: {
                "title": "番成立直前の感想と、今後の展望",
                "description": """
この5か月を振り返って、もっとも密度を高め合えた相手は誰か？
そして君は、番としてどのような未来を築きたいと願う？
                """
            }
        }
        
        # テーマ表示
        theme_text = gr.Textbox(
            value=f"今月のテーマ: {workshop_themes[game_state.turn]['title']}",
            label="テーマ",
            interactive=False
        )
        theme_description = gr.Textbox(
            value=workshop_themes[game_state.turn]['description'],
            label="テーマの説明",
            interactive=False
        )
        
        # 描写表示エリア
        workshop_area = gr.Textbox(label="ワークショップ描写", lines=20)
        
        # 感情変化表示エリア
        emotion_changes = gr.Textbox(label="感情変化", lines=5)
        
        # エネルギー表示（読み取り専用）
        energy_display = gr.Textbox(label="現在のノウアエネルギー", value=str(game_state.noua_energy))
        
        # 生成ボタン
        generate_btn = gr.Button("討論を生成（感情変化も自動適用）")
        
        # イベントハンドラ
        def generate_workshop():
            # 現在のテーマを取得
            current_theme = workshop_themes[game_state.turn]
            
            # 既に生成済みなら取得
            if game_state.turn in game_state.workshop_results:
                description = game_state.workshop_results[game_state.turn]["description"]
                emotion_text = game_state.workshop_results[game_state.turn].get("emotion_text", "感情変化情報がありません。")
                return (
                    description,
                    emotion_text,
                    str(game_state.noua_energy),
                    f"今月のテーマ: {current_theme['title']}",
                    current_theme['description']
                )
            
            # 現在の部屋割り情報を取得
            rooms_info = []
            for room_id, room in game_state.rooms.items():
                chars = []
                for char in room.occupants:
                    chars.append({
                        "name": char.name,
                        "role": room.roles[char.name]
                    })
                rooms_info.append({
                    "id": room_id,
                    "occupants": chars
                })
            
            # ワークショッププロンプトの構築
            characters_list = list(game_state.characters.values())
            
            try:
                description = llm_interface.generate_workshop(
                    llm_interface.build_workshop_prompt(current_theme, characters_list, rooms_info, game_state.turn)
                )
                
                # 感情変化を抽出して適用
                emotion_result = llm_interface.extract_emotion_changes(description)
                emotion_text = format_emotion_changes(emotion_result)
                
                # エネルギー再計算
                energy = game_state.calculate_noua_energy()
                game_state.noua_energy = energy
                
                # 結果を保存
                game_state.workshop_results[game_state.turn] = {
                    "description": description,
                    "emotion_changes": emotion_result,
                    "emotion_text": emotion_text,
                    "applied": True
                }
                
                return (
                    description,
                    emotion_text,
                    str(energy),
                    f"今月のテーマ: {current_theme['title']}",
                    current_theme['description']
                )
                
            except Exception as e:
                error_msg = f"エラー: {str(e)}"
                return (
                    error_msg,
                    "感情変化を生成できませんでした。",
                    str(game_state.noua_energy),
                    f"今月のテーマ: {current_theme['title']}",
                    current_theme['description']
                )
        
        # イベント関連付け
        generate_btn.click(
            fn=generate_workshop,
            inputs=[],
            outputs=[workshop_area, emotion_changes, energy_display, theme_text, theme_description]
        )
        
        def format_emotion_changes(emotion_result):
            """感情変化データを読みやすい形式に整形"""
            if "error" in emotion_result:
                return f"感情変化の抽出エラー: {emotion_result['error']}"
            
            if "emotion_changes" not in emotion_result or not emotion_result["emotion_changes"]:
                return "感情変化を抽出できませんでした。"
            
            emotion_text = "--- 感情変化の要約 ---\n"
            for change in emotion_result["emotion_changes"]:
                from_char = change["from"]
                to_char = change["to"]
                love_change = change["love_change"]
                hate_change = change["hate_change"]
                reason = change["reason"]
                
                # 符号の処理
                love_sign = "+" if love_change > 0 else ("-" if love_change < 0 else "±")
                hate_sign = "+" if hate_change > 0 else ("-" if hate_change < 0 else "±")
                
                # 絶対値を使用し、0の場合は0と表示
                love_value = abs(love_change) if love_change != 0 else 0
                hate_value = abs(hate_change) if hate_change != 0 else 0
                
                emotion_text += f"- {from_char} → {to_char}: {reason} (愛情{love_sign}{love_value}/憎悪{hate_sign}{hate_value})\n"
            
            return emotion_text
        
        # 次のフェーズへ進む関数
        def proceed_to_next_phase():
            if not game_state.workshop_results.get(game_state.turn, {}).get("applied", False):
                return "ワークショップの討論を生成してから次のフェーズに進んでください。"
            
            # フェーズを進める
            turn, phase = game_state.next_phase()
            
            # テーマを更新
            theme_text.update(value=f"今月のテーマ: {workshop_themes[game_state.turn]['title']}")
            theme_description.update(value=workshop_themes[game_state.turn]['description'])
            
            return f"次のフェーズに進みました。ターン{turn}、フェーズ{phase_name(phase)}"
        
        # イベント関連付け
        generate_btn.click(
            fn=generate_workshop,
            inputs=[],
            outputs=[workshop_area, emotion_changes, energy_display, theme_text, theme_description]
        )
        

def emotion_scan_ui(game_state, turn_display):  # turn_displayパラメータを追加
    with gr.Column():
        gr.Markdown("## 感情スキャン・評価フェーズ")
        gr.Markdown("各キャラクターの感情値と相互感情密度を評価します。")
        
        # 感情マトリックスの初期データを作成
        chars = list(game_state.characters.keys())
        matrix_data = []
        matrix_columns = ["キャラクター"]
        
        # カラム名を作成
        for char in chars:
            if char != chars[0]:  # 自分自身は除外
                matrix_columns.extend([f"{char}への愛情", f"{char}への憎悪"])
        
        # データを作成
        for from_char in chars:
            row_data = [from_char]  # キャラクター名
            for to_char in chars:
                if from_char != to_char:
                    love = game_state.characters[from_char].love_values.get(to_char, 0)
                    hate = game_state.characters[from_char].hate_values.get(to_char, 0)
                    row_data.extend([int(love), int(hate)])
            matrix_data.append(row_data)
        
        # DataFrameを作成
        emotion_df = pd.DataFrame(matrix_data, columns=matrix_columns)
        
        # 相互感情密度の初期データを作成
        density_data = []
        density_columns = ["キャラクター1", "キャラクター2", "相互感情密度", "番候補"]
        
        densities = game_state.calculate_emotion_density()
        for pair, value in densities.items():
            density_data.append([
                str(pair[0]),
                str(pair[1]),
                int(value),
                "✓" if value >= 100 else ""
            ])
        
        # 密度のDataFrameを作成
        density_df = pd.DataFrame(density_data, columns=density_columns)
        
        # データフレームの表示
        with gr.Accordion("感情マトリックス", open=True):
            emotion_matrix = gr.DataFrame(
                value=emotion_df,
                label="感情マトリックス",
                interactive=False
            )
        
        with gr.Accordion("相互感情密度", open=True):
            density_matrix = gr.DataFrame(
                value=density_df,
                label="相互感情密度",
                interactive=False
            )
        
        # エネルギー表示
        energy_value = gr.Number(label="ノウアエネルギー", value=int(game_state.noua_energy))
        
        # 番候補表示（最終ターンのみ）
        pair_data = []
        pair_columns = ["キャラクター1", "キャラクター2", "種類", "相互感情密度"]
        
        if game_state.turn >= 5:
            pairs, _ = game_state.calculate_pairs()
            for pair in pairs:
                char1, char2 = pair["characters"]
                pair_data.append([
                    str(char1),
                    str(char2),
                    str(pair["type"]),
                    int(pair["density"])
                ])
        
        pair_df = pd.DataFrame(pair_data, columns=pair_columns)
        pair_candidates = gr.DataFrame(
            value=pair_df,
            label="番候補",
            interactive=False
        )
        
        # 結果表示エリア
        result_text = gr.Textbox(label="結果", interactive=False)
        
        # ボタンエリア
        with gr.Row():
            # 更新ボタン
            update_btn = gr.Button("感情データを更新")
            # 次のターンへ進むボタン（最終ターン以外で表示）
            if game_state.turn < 5:
                next_turn_btn = gr.Button("次のターンへ")
        
        # イベントハンドラ
        def update_emotion_data():
            # 感情マトリックスの更新データ
            matrix_data = []
            for from_char in chars:
                row_data = [from_char]
                for to_char in chars:
                    if from_char != to_char:
                        love = game_state.characters[from_char].love_values.get(to_char, 0)
                        hate = game_state.characters[from_char].hate_values.get(to_char, 0)
                        row_data.extend([int(love), int(hate)])
                matrix_data.append(row_data)
            
            updated_emotion_df = pd.DataFrame(matrix_data, columns=matrix_columns)
            
            # 相互感情密度の更新データ
            density_data = []
            densities = game_state.calculate_emotion_density()
            for pair, value in densities.items():
                density_data.append([
                    str(pair[0]),
                    str(pair[1]),
                    int(value),
                    "✓" if value >= 100 else ""
                ])
            
            updated_density_df = pd.DataFrame(density_data, columns=density_columns)
            
            # エネルギー計算
            energy = int(game_state.calculate_noua_energy())
            
            # 番候補の更新データ
            pair_data = []
            if game_state.turn >= 5:
                pairs, _ = game_state.calculate_pairs()
                for pair in pairs:
                    char1, char2 = pair["characters"]
                    pair_data.append([
                        str(char1),
                        str(char2),
                        str(pair["type"]),
                        int(pair["density"])
                    ])
            
            updated_pair_df = pd.DataFrame(pair_data, columns=pair_columns)
            
            return updated_emotion_df, updated_density_df, energy, updated_pair_df
        
        # 次のターンに進む関数
        def proceed_to_next_turn():
            if game_state.turn >= 5:
                return "これ以上ターンを進めることはできません。", f"ターン {game_state.turn}/5"
            
            # ターンを進める（フェーズは1に戻す）
            game_state.turn += 1
            game_state.phase = 1
            
            # 部屋の割り当てをリセット
            for room in game_state.rooms.values():
                room.occupants = []
                room.roles = {}
            
            return f"ターン{game_state.turn}に進みました。新しい部屋割りを行ってください。", f"ターン {game_state.turn}/5"
        
        # イベント関連付け
        # 更新ボタンのイベント
        update_btn.click(
            fn=update_emotion_data,
            inputs=[],
            outputs=[emotion_matrix, density_matrix, energy_value, pair_candidates]
        )
        
        # 次のターンへ進むボタンのイベント（最終ターン以外で表示）
        if game_state.turn < 5:
            next_turn_btn.click(
                fn=proceed_to_next_turn,
                inputs=[],
                outputs=[result_text, turn_display]  # メインUIのターン表示を更新
            )

# メインアプリケーション
def main():
    # 設定読み込み
    config = load_config()
    
    # ゲーム状態初期化
    game_state = GameState()
    characters = load_characters()
    game_state.initialize_characters(characters)
    game_state.initialize_rooms(3)
    
    # LLMインターフェース初期化
    llm_interface = LLMInterface("config.ini")
    
    # Gradio UI構築
    with gr.Blocks(title="Pair Protocol") as app:
        gr.Markdown("# Pair Protocol: 感情密度選抜計画")
        gr.Markdown("感情倫理国家「ノウア連合」の中枢AI「セントリクス」として、最適な番を形成しましょう。")
        
        # ターン表示
        with gr.Row():
            turn_display = gr.Textbox(
                label="現在のターン",
                value=f"ターン {game_state.turn}/5",
                interactive=False,
                container=False,
                scale=1
            )
        
        # タブで各フェーズを切り替え
        with gr.Tabs() as tabs:
            # 部屋割りフェーズタブ
            with gr.Tab("部屋割りフェーズ"):
                room_assignment_ui(game_state)
            
            # 共同生活フェーズタブ
            with gr.Tab("共同生活フェーズ", interactive=lambda: all(room.occupants for room in game_state.rooms.values())):
                common_life_ui(game_state, llm_interface)
            
            # 感情ワークショップタブ
            with gr.Tab("感情ワークショップ", interactive=lambda: all(room.id in game_state.life_results.get(game_state.turn, {}) for room in game_state.rooms.values())):
                workshop_ui(game_state, llm_interface)
            
            # 感情スキャンタブ
            with gr.Tab("感情スキャン", interactive=lambda: game_state.turn in game_state.workshop_results):
                emotion_scan_ui(game_state, turn_display)
        
        # セーブ・ロードボタン
        with gr.Row():
            save_btn = gr.Button("ゲームを保存")
            load_btn = gr.Button("ゲームをロード")
            save_filename = gr.Textbox(label="保存ファイル名", value="")
            load_filename = gr.Dropdown(label="ロードするファイル", choices=list_save_files())
        
        # セーブ・ロード処理の関連付け
        save_btn.click(
            fn=lambda fn: game_state.save_game(fn if fn else None)[1],
            inputs=[save_filename],
            outputs=[gr.Textbox(label="結果")]
        )
        
        load_btn.click(
            fn=lambda fn: game_state.load_game(os.path.join("./data/saves", fn))[1],
            inputs=[load_filename],
            outputs=[gr.Textbox(label="結果")]
        )
    
    # アプリケーション起動
    app.launch()

# エントリーポイント
if __name__ == "__main__":
    main()