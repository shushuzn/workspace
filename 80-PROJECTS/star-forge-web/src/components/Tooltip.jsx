import { useState } from 'react';
import styles from './Tooltip.module.css';

export default function Tooltip({ children, text }) {
  const [show, setShow] = useState(false);

  return (
    <div className={styles.container}
      onMouseEnter={() => setShow(true)}
      onMouseLeave={() => setShow(false)}>
      {children}
      {show && <div className={styles.tooltip}>{text}</div>}
    </div>
  );
}
