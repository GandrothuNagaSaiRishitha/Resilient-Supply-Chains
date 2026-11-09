import axios from 'axios'
import { apiEndpoints } from './apiEndpoints'
import { getApiBaseUrl } from './apiConfig'

const accessTokenStorageKey = 'supplymind.accessToken'

interface DemoLoginResponse {
  access_token: string
}

let pendingTokenRequest: Promise<string> | undefined

export async function getAccessToken(): Promise<string> {
  const storedToken = window.sessionStorage.getItem(accessTokenStorageKey)
  if (storedToken) return storedToken

  const baseURL = getApiBaseUrl()
  if (baseURL === undefined) {
    throw new Error('VITE_API_BASE_URL is required to authenticate with the API.')
  }

  if (!pendingTokenRequest) {
    pendingTokenRequest = axios
      .post<DemoLoginResponse>(apiEndpoints.demoLogin, undefined, {
        baseURL,
        timeout: Number(import.meta.env.VITE_API_TIMEOUT_MS) || 15_000,
        headers: { Accept: 'application/json' },
      })
      .then(({ data }) => {
        if (typeof data.access_token !== 'string' || data.access_token.length === 0) {
          throw new Error('The demo login response did not include an access token.')
        }
        window.sessionStorage.setItem(accessTokenStorageKey, data.access_token)
        return data.access_token
      })
      .finally(() => {
        pendingTokenRequest = undefined
      })
  }

  return pendingTokenRequest
}
