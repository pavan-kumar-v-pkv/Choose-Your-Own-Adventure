import { useState } from 'react'

function ThemeInput({ onSubmit }) {
    const [theme, setTheme] = useState('');
    const [error, setError] = useState('');

    const handleSubmit = (e) => {
        e.preventDefault();

        if (!theme.trim()) {
            setError('Theme cannot be empty.');
            return
        }

        onSubmit(theme);
    }

    return (
        <div className="theme-input-container">
            <h2>Generate Your Own Adventure</h2>
            <p>Enter a theme for your interactive story:</p>

            <form onSubmit={handleSubmit}>
                <div className={"input-group"}>
                    <input
                        type="text"
                        value={theme}
                        onChange={(e) => setTheme(e.target.value)}
                        placeholder="Enter theme..."
                        className={error ? 'error' : ''}
                    />
                    {error && <p className="error-message">{error}</p>}
                </div>
                <button type="submit" className="generate-btn">Generate Story</button>
            </form>
        </div>
    )
}

export default ThemeInput;