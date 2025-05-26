const errorHandler = (err, req, res, next) => {
    console.error('❌ Error:', err.stack);
    res.status(500).json({ message: err.message || 'Server Error' });
  };
  
  export default errorHandler;