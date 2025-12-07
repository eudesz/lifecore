import type { AppProps } from 'next/app'
import Head from 'next/head'
import { useRouter } from 'next/router'
import '../styles/globals.css'
import { AuthProvider } from '@/context/AuthContext'
import Navbar from '@/components/layout/Navbar'

export default function App({ Component, pageProps }: AppProps) {
  const router = useRouter()
  
  // Páginas que NO deben mostrar el Navbar (landing page)
  const pagesWithoutNavbar = ['/', '/doctor/[token]', '/d/[token]', '/chat']
  const showNavbar = !pagesWithoutNavbar.includes(router.pathname)

  if (process.env.NODE_ENV === 'development' && typeof window !== 'undefined') {
    // Dev-only a11y; avoid bundler resolution so build doesn't require the dep
    // eslint-disable-next-line @typescript-eslint/no-floating-promises
    (async () => {
      try {
        const importAxe: any = (new Function('return import("@axe-core/react")'))
        const importReact: any = (new Function('return import("react")'))
        const [axeMod, reactMod] = await Promise.all([importAxe(), importReact()])
        const axe = (axeMod as any).default || (axeMod as any)
        const ReactAny = (reactMod as any).default || (reactMod as any)
        axe(ReactAny, window, 1000)
      } catch {
        // silently ignore if module not present
      }
    })()
  }
  
  return (
    <AuthProvider>
      <Head>
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <meta name="color-scheme" content="light dark" />
        <title>QuantIA - Your Personal Health Assistant</title>
      </Head>
      {showNavbar && <Navbar />}
      <Component {...pageProps} />
    </AuthProvider>
  )
}


