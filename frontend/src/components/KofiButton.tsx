// src/components/KofiButton.tsx
export default function KofiButton() {
    return (
        <div className="fixed bottom-6 right-6">
            <a
                href="https://ko-fi.com/YOUR_KOFI_USERNAME"
                target="_blank"
                rel="noopener noreferrer"
                className="bg-[#3A7DFF] hover:bg-[#316BDF] text-white w-12 h-12 rounded-full flex items-center justify-center shadow-lg transition-colors"
            >
                <span className="sr-only">Support on Ko-fi</span>
                {/* Coffee cup icon */}
                <svg
                    xmlns="http://www.w3.org/2000/svg"
                    width="24"
                    height="24"
                    viewBox="0 0 24 24"
                    fill="none"
                    stroke="currentColor"
                    strokeWidth="2"
                    strokeLinecap="round"
                    strokeLinejoin="round"
                >
                    <path d="M17 8h1a4 4 0 1 1 0 8h-1" />
                    <path d="M3 8h14v9a4 4 0 0 1-4 4H7a4 4 0 0 1-4-4Z" />
                    <line x1="6" y1="2" x2="6" y2="4" />
                    <line x1="10" y1="2" x2="10" y2="4" />
                    <line x1="14" y1="2" x2="14" y2="4" />
                </svg>
            </a>
        </div>
    );
}