// useFormatting.js
export default function useFormatting() {
    const formatFeatureName = (name) => {
      return name
        .replace(/_/g, ' ')
        .split(' ')
        .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
        .join(' ');
    };
  
    return {
      formatFeatureName
    };
  }