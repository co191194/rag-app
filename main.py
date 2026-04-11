import os
from openai import OpenAI
from dotenv import load_dotenv

# .envから環境変数を読み込む
load_dotenv()

# OpenAIクライアントの初期化
client = OpenAI()


def chat_with_ai(prompt):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant. Answer the user's questions concisely.",
            },
            {"role": "user", "content": prompt},
        ],
    )
    return response.choices[0].message.content


if __name__ == "__main__":
    print("--- AIチャットテスト環境 ---")
    print("終了するには 'exit' と入力してください。\n")

    while True:
        user_input = input("あなた: ")
        if user_input.lower() in ["exit", "quit"]:
            print("チャットを終了します。")
            break

        # 空の入力を無視する
        if not user_input.strip():
            continue

        try:
            answer = chat_with_ai(user_input)
            print(f"\nAI: {answer}\n")
        except Exception as e:
            print(f"\nエラーが発生しました: {e}\n")
