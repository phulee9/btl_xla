import React, { useState, useRef } from 'react';
import './App.css';

function App() {
    const [selectedImage, setSelectedImage] = useState(null);
    const [previewUrl, setPreviewUrl] = useState(null);
    const [results, setResults] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const fileInputRef = useRef(null);

    const handleImageSelect = (e) => {
        const file = e.target.files[0];
        if (file) {
            setSelectedImage(file);
            setPreviewUrl(URL.createObjectURL(file));
            setError(null);
        }
    };

    const handleSearch = async () => {
        if (!selectedImage) {
            setError('Vui lòng chọn hình ảnh!');
            return;
        }

        setLoading(true);
        setError(null);

        const formData = new FormData();
        formData.append('image', selectedImage);

        try {
            const response = await fetch('http://localhost:5000/api/search', {
                method: 'POST',
                body: formData,
            });

            const data = await response.json();

            if (data.success) {
                setResults(data.results);
            } else {
                setError(data.error || 'Có lỗi xảy ra');
            }
        } catch (err) {
            setError('Không thể kết nối đến server');
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    const handleImageClick = () => {
        fileInputRef.current.click();
    };

    const handleClear = () => {
        setSelectedImage(null);
        setPreviewUrl(null);
        setResults([]);
        setError(null);
        if (fileInputRef.current) {
            fileInputRef.current.value = '';
        }
    };

    return (
        <div className="App">
            {/* Header giống Shopee */}
            <header className="header">
                <div className="container">
                    <div className="header-content">
                        <h1 className="logo">Fashion Finder</h1>
                        <div className="header-subtitle">Tìm kiếm sản phẩm thời trang bằng hình ảnh</div>
                    </div>
                </div>
            </header>

            {/* Search Section */}
            <div className="search-section">
                <div className="container">
                    <div className="search-box">
                        <input
                            type="file"
                            ref={fileInputRef}
                            onChange={handleImageSelect}
                            accept="image/*"
                            style={{ display: 'none' }}
                        />

                        <div className="upload-area" onClick={handleImageClick}>
                            {previewUrl ? (
                                <div className="preview-container">
                                    <img src={previewUrl} alt="Preview" className="preview-image" />
                                    <button className="clear-btn" onClick={(e) => { e.stopPropagation(); handleClear(); }}>
                                        ✕
                                    </button>
                                </div>
                            ) : (
                                <div className="upload-placeholder">
                                    <svg className="upload-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                                    </svg>
                                    <p className="upload-text">Nhấn để chọn hình ảnh</p>
                                    <p className="upload-subtext">hoặc kéo thả hình ảnh vào đây</p>
                                </div>
                            )}
                        </div>

                        <button
                            className="search-btn"
                            onClick={handleSearch}
                            disabled={loading || !selectedImage}
                        >
                            {loading ? (
                                <>
                                    <span className="spinner"></span>
                                    Đang tìm kiếm...
                                </>
                            ) : (
                                <>
                                    <svg className="search-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                                        <circle cx="11" cy="11" r="8"></circle>
                                        <path d="m21 21-4.35-4.35"></path>
                                    </svg>
                                    Tìm kiếm
                                </>
                            )}
                        </button>
                    </div>

                    {error && (
                        <div className="error-message">
                            ⚠️ {error}
                        </div>
                    )}
                </div>
            </div>

            {/* Results Section */}
            {results.length > 0 && (
                <div className="results-section">
                    <div className="container">
                        <h2 className="results-title">Sản phẩm tương tự</h2>
                        <div className="results-grid">
                            {results.map((result, index) => {
                                // Xử lý đường dẫn ảnh
                                let imagePath = result.image;

                                // Nếu đường dẫn không bắt đầu bằng http hoặc /, thêm vào
                                if (!imagePath.startsWith('http') && !imagePath.startsWith('/')) {
                                    imagePath = `/${imagePath}`;
                                }

                                const imageUrl = imagePath.startsWith('http')
                                    ? imagePath
                                    : `http://localhost:5000${imagePath}`;

                                return (
                                    <div key={index} className="product-card">
                                        <div className="product-image-wrapper">
                                            <img
                                                src={imageUrl}
                                                alt={`Product ${index + 1}`}
                                                className="product-image"
                                                onError={(e) => {
                                                    console.error('Image load error:', imageUrl);
                                                    e.target.src = 'https://via.placeholder.com/300x300?text=Image+Not+Found';
                                                }}
                                            />
                                        </div>
                                        <div className="product-info">
                                            <div className="similarity-badge">
                                                {(result.similarity * 100).toFixed(0)}% tương đồng
                                            </div>
                                        </div>
                                    </div>
                                );
                            })}
                        </div>
                    </div>
                </div>
            )}

            {/* Footer */}
            <footer className="footer">
                <div className="container">
                    <p>© 2025 Fashion Finder - Tìm kiếm thời trang thông minh</p>
                </div>
            </footer>
        </div>
    );
}

export default App;