import { mount, flushPromises } from '@vue/test-utils'
import { describe, it, expect, vi } from "vitest"
import axios from 'axios'
import App from './App.vue'
import { nextTick } from 'vue'

//////////////////////////////////////////////////////////////////
// モックの設定
//////////////////////////////////////////////////////////////////

// axiosのモックを設定
vi.mock('axios')


//////////////////////////////////////////////////////////////////
// テストケース
//////////////////////////////////////////////////////////////////

describe('App.vueのテスト', () => {
    it('初期画面が正しくレンダリングされ、タイトルが表示されること', () => {
        // コンポーネントをマウント
        const wrapper = mount(App)

        // 検証
        expect(wrapper.text()).toContain('社内ドキュメントAIアシスタント')
        expect(wrapper.find('input[type="file"]').exists()).toBe(true)
    })

    it('質問を送信するとローディング表示になり、回答が表示されること', async () => {
        // モックのレスポンスを設定
        const mockedAxios = vi.mocked(axios)

        let resolveApi!: (value: { data: { answer: string } }) => void
        const pendingPromise = new Promise<{ data: { answer: string } }>((resolve) => {
            resolveApi = resolve as typeof resolveApi
        })
        mockedAxios.post.mockReturnValueOnce(pendingPromise)

        const wrapper = mount(App)

        // 質問を入力
        const input = wrapper.find('input[placeholder="質問を入力してください..."]')
        await input.setValue('就業規則について教えて')

        // 送信ボタンをクリック
        const buttons = wrapper.findAll('button')
        const sendButton = buttons.find(btn => btn.text() === '送信')
        if (!sendButton) {
            throw new Error('送信ボタンが見つかりませんでした。')
        }
        await sendButton.trigger('click')
        await nextTick()

        // ローディング表示を確認
        const loadingMessage = 'AIが回答を生成中...'
        expect(wrapper.text()).toContain(loadingMessage)

        // 非同期処理が完了するのを待つ
        resolveApi({
            data: { answer: 'これはモックされた回答です。' }
        })
        await flushPromises()

        // モックされた回答が表示されることを確認
        expect(wrapper.text()).not.toContain(loadingMessage)
        expect(wrapper.text()).toContain('これはモックされた回答です。')
    })
})