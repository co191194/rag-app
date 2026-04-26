<script setup lang="ts">
import { ref } from "vue";
import axios from "axios";
import { Button } from "./components/ui/button";
import { Input } from "./components/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "./components/ui/card";
import { ScrollArea } from "./components/ui/scroll-area";

// 型定義
interface Message {
  role: "user" | "ai";
  content: string;
}

const query = ref<string>("");
const messages = ref<Message[]>([]);
const isLoading = ref<boolean>(false);
const fileInput = ref<HTMLInputElement | null>(null);

// APIのベースURL
const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

/**
 * ファイルアップロードのハンドラーです。
 *
 * @param event イベント
 */
const handleUpload = async (event: Event) => {
  const target = event.target as HTMLInputElement;
  if (!target.files?.length) return;

  const formData = new FormData();
  formData.append("file", target.files[0]);

  try {
    const res = await axios.post(`${API_URL}/upload`, formData, {
      headers: { "Content-Type": "multipart/form-data" },
    });
    alert(res.data.message);
  } catch (error) {
    console.error("ファイルのアップロードに失敗しました:", error);
    alert("ファイルのアップロードに失敗しました。");
  } finally {
    // ファイル入力をリセット
    if (fileInput.value) {
      fileInput.value.value = "";
    }
  }
};

const keydownHandler = (event: KeyboardEvent) => {
  if (event.isComposing) return; // 日本語入力中は無視
  if (event.key === "Enter" && !event.shiftKey) {
    event.preventDefault();
    sendQuery();
  }
};

const sendQuery = async () => {
  if (!query.value.trim()) return;

  const userMessage = query.value.trim();

  // ユーザーメッセージを追加
  messages.value.push({ role: "user", content: userMessage });
  query.value = "";
  isLoading.value = true;

  try {
    const res = await axios.post(`${API_URL}/chat`, { query: userMessage });
    messages.value.push({ role: "ai", content: res.data.answer });
  } catch (error) {
    console.error("チャットの送信に失敗しました:", error);
    alert("チャットの送信に失敗しました。");
  } finally {
    isLoading.value = false;
  }
};
</script>

<template>
  <div class="min-h-screen bg-slate-50 p-4 md:p-8">
    <div class="max-w-3xl mx-auto space-y-6">
      <Card>
        <CardHeader>
          <CardTitle>社内ドキュメントAIアシスタント</CardTitle>
        </CardHeader>
        <CardContent>
          <div class="flex items-center gap-4">
            <Input
              type="file"
              accept=".pdf"
              @change="handleUpload"
              class="cursor-pointer"
            />
            <p class="text-xs text-slate-500">
              就業規則などのPDFをアップロードしてください
            </p>
          </div>
        </CardContent>
      </Card>

      <Card class="h-125 flex flex-col">
        <ScrollArea class="flex-1 min-h-0 p-4">
          <div
            v-for="(msg, i) in messages"
            :key="i"
            :class="[
              'mb-4 flex',
              msg.role === 'user' ? 'justify-end' : 'justify-start',
            ]"
          >
            <div
              :class="[
                'max-w-[80%] rounded-lg p-3 text-sm',
                msg.role === 'user'
                  ? 'bg-primary text-primary-foreground'
                  : 'bg-muted',
              ]"
            >
              {{ msg.content }}
            </div>
          </div>
          <div v-if="isLoading" class="text-slate-400 text-xs italic">
            AIが回答を生成中...
          </div>
        </ScrollArea>

        <div class="p-4 border-t flex gap-2">
          <Input
            v-model="query"
            placeholder="質問を入力してください..."
            @keydown="keydownHandler"
          />
          <Button @click="sendQuery" :disabled="isLoading">送信</Button>
        </div>
      </Card>
    </div>
  </div>
</template>
