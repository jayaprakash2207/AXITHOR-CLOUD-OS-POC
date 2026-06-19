import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'Axithor Cloud OS',
  description: 'Bring Your Own Cloud hosting for static websites on Google Drive.',
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
