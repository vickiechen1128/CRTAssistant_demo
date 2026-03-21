import { useEffect } from 'react';

/**
 * 消息提示组件
 * @param {string} type - 类型: info, success, warning, error
 * @param {string} message - 消息内容
 * @param {function} onClose - 关闭回调
 * @param {number} duration - 自动关闭时间（毫秒），默认 3000
 */
export function Message({ type = 'info', message, onClose, duration = 3000 }) {
  useEffect(() => {
    if (duration > 0 && onClose) {
      const timer = setTimeout(onClose, duration);
      return () => clearTimeout(timer);
    }
  }, [duration, onClose]);

  if (!message) return null;

  return (
    <div className={`message ${type}`}>
      {message}
    </div>
  );
}
