import { useState } from 'react';
import styles from './FloatButton.module.css';

export default function FloatButton({ icon, onClick, position = 'right' }) {
  const [show, setShow] = useState(true);

  return (
    show && (
      <button className={`${styles.btn} ${styles[position]}`} onClick={onClick}>
        {icon}
      </button>
    )
  );
}
