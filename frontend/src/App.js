import React, { useState } from 'react';
import './App.css';

function App() {
    const [url, setUrl] = useState('');
    const [formats, setFormats] = useState([]);
    const [selectedFormat, setSelectedFormat] = useState('');
    const [downloadUrl, setDownloadUrl] = useState('');
    const [error, setError] = useState('');

    const fetchFormats = async (event) => {
        event.preventDefault();
        setError('');
        try {
            const response = await fetch('/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: new URLSearchParams({ url }),
            });
            if (!response.ok) {
                throw new Error('Failed to fetch formats');
            }
            const data = await response.json();
            setFormats(data.formats);
        } catch (error) {
            setError(error.message);
        }
    };

    const downloadVideo = async (event) => {
        event.preventDefault();
        setError('');
        try {
            const response = await fetch('/download', {
                method: 'POST',
                body: new URLSearchParams({
                    url: downloadUrl,
                    format_id: selectedFormat,
                }),
            });
            if (!response.ok) {
                throw new Error('Failed to download video');
            }
            const data = await response.json();
            if (data.filename) {
                const link = document.createElement('a');
                link.href = `/get_file/${data.filename}`;
                link.download = data.filename;
                link.textContent = 'Click here to download';
                document.body.appendChild(link);
            }
        } catch (error) {
            setError(error.message);
        }
    };

    return (
        <div className="App">
            <h1>YouTube Video Downloader</h1>
            {error && <div className="error">{error}</div>}
            <form onSubmit={fetchFormats}>
                <input
                    type="text"
                    value={url}
                    onChange={(e) => setUrl(e.target.value)}
                    placeholder="Enter YouTube URL"
                    required
                />
                <button type="submit">Get Formats</button>
            </form>
            {formats.length > 0 && (
                <form onSubmit={downloadVideo}>
                    <input
                        type="hidden"
                        value={url}
                        onChange={(e) => setDownloadUrl(e.target.value)}
                    />
                    <select
                        value={selectedFormat}
                        onChange={(e) => setSelectedFormat(e.target.value)}
                    >
                        {formats.map((format) => (
                            <option key={format.format_id} value={format.format_id}>
                                {format.resolution} ({format.ext})
                            </option>
                        ))}
                    </select>
                    <button type="submit">Download</button>
                </form>
            )}
        </div>
    );
}

export default App;
