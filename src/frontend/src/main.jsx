import React from 'react'
import { createRoot } from 'react-dom/client'
import Home from './pages/index.jsx'

function App() {
	return (
		<div className="min-h-screen">
			<Home />
		</div>
	)
}

createRoot(document.getElementById('root')).render(
	<React.StrictMode>
		<App />
	</React.StrictMode>
)
