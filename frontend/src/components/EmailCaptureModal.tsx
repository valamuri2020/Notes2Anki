import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, AlertCircle } from 'lucide-react';

interface EmailCaptureModalProps {
  isOpen: boolean;
  onClose: () => void;
  onEmailSubmit: (email: string) => void;
}

// RFC 5322 compliant email regex
const EMAIL_REGEX = /^[a-zA-Z0-9._%+-]+@(?!(\d+\.)+\d+$)([a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}$/;

export default function EmailCaptureModal({ isOpen, onClose, onEmailSubmit}: EmailCaptureModalProps) {
  const [email, setEmail] = useState('');
  const [isValid, setIsValid] = useState(true);
  const [isTouched, setIsTouched] = useState(false);

  const validateEmail = (email: string) => {
    return EMAIL_REGEX.test(email);
  };

  const handleEmailChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newEmail = e.target.value;
    setEmail(newEmail);
    setIsTouched(true);
    setIsValid(validateEmail(newEmail));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (email.trim() && validateEmail(email)) {
      onEmailSubmit(email);
    } else {
      setIsValid(false);
    }
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 bg-black/50 flex items-center justify-center p-4"
        >
          <motion.div
            initial={{ scale: 0.9, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0.9, opacity: 0 }}
            className="bg-white rounded-xl p-6 max-w-md w-full relative"
          >
            <button
              onClick={onClose}
              className="absolute top-4 right-4 text-gray-400 hover:text-gray-600"
            >
              <X className="w-5 h-5" />
            </button>

            <h3 className="text-xl font-semibold mb-4">Almost there!</h3>
            <p className="text-gray-600 mb-6">
              Enter your email to download your flashcards. We'll occasionally send helpful study resources. No spam, that's a promise!
            </p>

            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="relative">
                <input
                  type="email"
                  value={email}
                  onChange={handleEmailChange}
                  onBlur={() => setIsTouched(true)}
                  placeholder="Enter your email"
                  className={`w-full px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 transition-colors
                    ${isTouched && !isValid 
                      ? 'border-red-500 focus:ring-red-500/20' 
                      : 'border-gray-300 focus:ring-[#3A7DFF] focus:border-transparent'
                    }`}
                />
                {isTouched && !isValid && (
                  <div className="absolute right-3 top-1/2 -translate-y-1/2 text-red-500">
                    <AlertCircle className="w-5 h-5" />
                  </div>
                )}
              </div>
              {isTouched && !isValid && (
                <p className="text-red-500 text-sm -mt-2">
                  Please enter a valid email address
                </p>
              )}

              <div className="flex flex-col gap-3">
                <button
                  type="submit"
                  className="bg-[#3A7DFF] hover:bg-[#316BDF] text-white px-4 py-2 rounded-lg font-medium transition-colors"
                >
                  Submit & Download
                </button>
              </div>
            </form>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
} 