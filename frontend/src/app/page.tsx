// src/app/page.tsx
"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import FileUpload from "@/components/FileUpload";
import Header from "@/components/Header";
import CreativeLoader from "@/components/ProcessingLoader";
import DownloadSection from "@/components/DownloadSection";
import KofiButton from "@/components/KofiButton";

export default function Home() {
  const [isProcessing, setIsProcessing] = useState(false);
  const [isDownloadReady, setIsDownloadReady] = useState(false);
  const [files, setFiles] = useState<File[]>([]);

  const handleSubmit = async () => {
    if (files.length === 0) return;

    setIsProcessing(true);
    // TODO: Implement actual file processing
    // Simulating processing time for demo
    setTimeout(() => {
      setIsProcessing(false);
      setIsDownloadReady(true);
    }, 10000);
  };

  return (
    <main className="min-h-screen px-4 py-8">
      <Header />

      <div className="max-w-4xl mx-auto mt-16">
        <AnimatePresence mode="wait">
          {!isProcessing && !isDownloadReady && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
            >
              <FileUpload
                files={files}
                setFiles={setFiles}
              />

              <div className="mt-8 flex justify-center">
                <motion.button
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  className={`px-8 py-3 rounded-lg text-white text-lg font-medium 
                    transition-colors shadow-lg shadow-blue-500/20
                    ${files.length === 0
                      ? 'bg-neutral-400 cursor-not-allowed'
                      : 'bg-[#3A7DFF] hover:bg-[#316BDF]'
                    }`}
                  onClick={handleSubmit}
                  disabled={files.length === 0}
                >
                  Generate Flashcards
                </motion.button>
              </div>
            </motion.div>
          )}

          {isProcessing && (
            <motion.div
              key="processing"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="glass-morphism rounded-xl p-12 flex justify-center"
            >
              <CreativeLoader />
            </motion.div>
          )}

          {isDownloadReady && (
            <DownloadSection />
          )}
        </AnimatePresence>
      </div>

      <KofiButton />
    </main>
  );
}