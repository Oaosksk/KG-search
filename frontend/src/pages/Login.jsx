import { useGoogleLogin } from '@react-oauth/google'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { authAPI } from '../services/api'
import './Login.css'

export default function Login() {
  const navigate = useNavigate()
  const { login } = useAuth()

  const handleGoogleLogin = useGoogleLogin({
    onSuccess: async (response) => {
      try {
        console.log('Google login success:', response)
        const { data } = await authAPI.googleLogin(response.access_token)
        console.log('Backend response:', data)
        login(data.access_token, data.user)
        navigate('/')
      } catch (error) {
        console.error('Login failed:', error)
        alert('Login failed: ' + error.message)
      }
    },
    onError: (error) => {
      console.error('Google login error:', error)
      alert('Google login failed')
    },
    scope: 'https://www.googleapis.com/auth/drive.readonly https://www.googleapis.com/auth/drive.file'
  })

  return (
    <div className="login-container">
      <div className="login-card">
        <h1>KG-Search</h1>
        <p>Knowledge Graph + RAG Search System</p>
        <button onClick={handleGoogleLogin} className="google-btn">
          Sign in with Google
        </button>
      </div>
    </div>
  )
}
