function LoadingStatus({theme}) {
  return (
    <div className="loading-container">
      <h2>Generating Your {theme} Story...</h2>
      <div className="loading-animation">
        <div className="spinner"></div>
      </div>

      <p className="loading-info">
        This may take a few moments. Please do not refresh or navigate away from the page.
      </p>
    </div>
  )
}

export default LoadingStatus;