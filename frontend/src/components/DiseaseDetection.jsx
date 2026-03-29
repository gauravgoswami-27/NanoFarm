import { useState, useRef } from 'react';

function DiseaseDetection({ executeWebhook }) {
  const [file, setFile] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);
  const [isDragging, setIsDragging] = useState(false);
  const fileInputRef = useRef(null);

  const handleValidFile = (selectedFile) => {
    if (selectedFile && selectedFile.type.startsWith('image/')) {
      setFile(selectedFile);
      const reader = new FileReader();
      reader.onloadend = () => setPreviewUrl(reader.result);
      reader.readAsDataURL(selectedFile);
    } else {
      alert("Please upload an image file.");
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files.length > 0) {
      handleValidFile(e.target.files[0]);
    }
  };

  const onDragOver = (e) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const onDragLeave = (e) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const onDrop = (e) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      handleValidFile(e.dataTransfer.files[0]);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) return;

    const formData = new FormData();
    formData.append('image', file);
    
    // Add a text prompt for the AI Agent handling the image 
    // This matches your {{ $json.body.message }} expectation in n8n!
    formData.append('message', 'Please act as an expert agronomist. Analyze this image of a plant leaf, identify the plant and detect any visible diseases. Please reply with only a JSON snippet containing "disease_name" and "treatment".');

    await executeWebhook(formData, true);
  };

  return (
    <div className="tab-content">
      <h2>Plant Disease Detection</h2>
      <p className="tab-description">Upload an image of a plant leaf to identify diseases and get treatment advice.</p>
      
      <form onSubmit={handleSubmit} className="dynamic-form">
        <div 
          className={`file-upload-container ${isDragging ? 'drag-over' : ''}`}
          onDragOver={onDragOver}
          onDragLeave={onDragLeave}
          onDrop={onDrop}
          onClick={() => fileInputRef.current.click()}
        >
          <div className="upload-icon">📸</div>
          <p>Drag & Drop your image here or</p>
          <span className="file-label">Browse Files</span>
          <input 
            type="file" 
            accept="image/*" 
            className="hidden-input" 
            ref={fileInputRef}
            onChange={handleFileChange}
            onClick={(e) => e.stopPropagation()} 
          />
          
          {file && <div className="file-name">{file.name}</div>}
          {previewUrl && <img src={previewUrl} alt="Preview" className="image-preview" />}
        </div>
        <button type="submit" className="submit-btn" disabled={!file}>Analyze Image</button>
      </form>
    </div>
  );
}

export default DiseaseDetection;
