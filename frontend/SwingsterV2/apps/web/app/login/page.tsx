import { login, signup, loginWithGoogle } from './actions'
import { LiquidEther } from '@/components/ui/liquid-ether'
import Link from 'next/link'

export default function LoginPage() {
  return (
    <main className="min-h-screen flex items-center justify-center relative overflow-hidden bg-surface">
      {/* ── Global Liquid Ether Background ── */}
      <div className="fixed inset-0 z-0 opacity-40 mix-blend-screen pointer-events-none">
        <LiquidEther
          colors={['#10b981', '#059669', '#ef4444']}
          mouseForce={30}
          cursorSize={150}
          isViscous={true}
          viscous={25}
          resolution={0.4}
        />
      </div>

      <div className="relative z-10 w-full max-w-md p-8 md:p-10 rounded-3xl bg-[#0c0c10]/80 backdrop-blur-xl border border-white/10 shadow-[0_0_50px_rgba(16,185,129,0.1)]">
        
        <div className="mb-8 text-center">

          <h1 className="text-2xl font-bold text-white mb-2">Welcome Back</h1>
          <p className="text-white/60">Sign in to your account to continue.</p>
        </div>

        <form className="flex flex-col gap-4">
          <button 
            formAction={loginWithGoogle}
            formNoValidate
            className="w-full flex items-center justify-center gap-3 py-3.5 bg-white text-black hover:bg-gray-100 font-bold rounded-lg transition-all duration-300 shadow-[0_0_15px_rgba(255,255,255,0.1)] mb-2"
          >
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48" width="20px" height="20px">
              <path fill="#FFC107" d="M43.611,20.083H42V20H24v8h11.303c-1.649,4.657-6.08,8-11.303,8c-6.627,0-12-5.373-12-12c0-6.627,5.373-12,12-12c3.059,0,5.842,1.154,7.961,3.039l5.657-5.657C34.046,6.053,29.268,4,24,4C12.955,4,4,12.955,4,24c0,11.045,8.955,20,20,20c11.045,0,20-8.955,20-20C44,22.659,43.862,21.35,43.611,20.083z"/>
              <path fill="#FF3D00" d="M6.306,14.691l6.571,4.819C14.655,15.108,18.961,12,24,12c3.059,0,5.842,1.154,7.961,3.039l5.657-5.657C34.046,6.053,29.268,4,24,4C16.318,4,9.656,8.337,6.306,14.691z"/>
              <path fill="#4CAF50" d="M24,44c5.166,0,9.86-1.977,13.409-5.192l-6.19-5.238C29.211,35.091,26.715,36,24,36c-5.202,0-9.619-3.317-11.283-7.946l-6.522,5.025C9.505,39.556,16.227,44,24,44z"/>
              <path fill="#1976D2" d="M43.611,20.083H42V20H24v8h11.303c-0.792,2.237-2.231,4.166-4.087,5.571c0.001-0.001,0.002-0.001,0.003-0.002l6.19,5.238C36.971,39.205,44,34,44,24C44,22.659,43.862,21.35,43.611,20.083z"/>
            </svg>
            Continue with Google
          </button>

          <div className="relative mb-2">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-white/10"></div>
            </div>
            <div className="relative flex justify-center text-sm">
              <span className="px-2 bg-[#0c0c10] text-white/40">Or continue with email</span>
            </div>
          </div>

          <div className="space-y-1">
            <label htmlFor="email" className="text-sm font-medium text-white/80">Email</label>
            <input 
              id="email" 
              name="email" 
              type="email" 
              placeholder="you@example.com"
              required 
              className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-3 text-white placeholder:text-white/30 focus:outline-none focus:border-emerald-500/50 focus:ring-1 focus:ring-emerald-500/50 transition-all"
            />
          </div>
          
          <div className="space-y-1 mb-2">
            <label htmlFor="password" className="text-sm font-medium text-white/80">Password</label>
            <input 
              id="password" 
              name="password" 
              type="password"
              placeholder="••••••••" 
              required 
              className="w-full bg-white/5 border border-white/10 rounded-lg px-4 py-3 text-white placeholder:text-white/30 focus:outline-none focus:border-emerald-500/50 focus:ring-1 focus:ring-emerald-500/50 transition-all"
            />
          </div>

          <button 
            formAction={login} 
            className="w-full py-3.5 bg-emerald-500 hover:bg-emerald-400 text-black font-bold rounded-lg transition-all duration-300 shadow-[0_0_15px_rgba(16,185,129,0.3)] mt-2"
          >
            Log in
          </button>
          
          <div className="relative mt-2 mb-2">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-white/10"></div>
            </div>
            <div className="relative flex justify-center text-sm">
              <span className="px-2 bg-[#0c0c10] text-white/40">New to Swingster?</span>
            </div>
          </div>

          <button 
            formAction={signup} 
            className="w-full py-3.5 bg-white/5 hover:bg-white/10 text-white font-bold rounded-lg border border-white/10 transition-all duration-300"
          >
            Create an account
          </button>
        </form>
      </div>
    </main>
  )
}
