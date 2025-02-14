"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import FileUpload from "@/components/FileUpload";

import Header from "@/components/Header";
import ProcessingLoader from "../components/ProcessingLoader";
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
    }, 3000);
  };

  return (
    <main className="min-h-screen px-4 py-8">
      <Header />

      <div className="max-w-4xl mx-auto mt-16">
        <FileUpload
          files={files}
          setFiles={setFiles}
        />

        <div className="mt-8 flex justify-center">
          <AnimatePresence mode="wait">
            {!isProcessing && !isDownloadReady && (
              <motion.button
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className={`px-8 py-3 rounded-lg text-white text-lg font-medium transition-colors
                  ${files.length === 0
                    ? 'bg-neutral-400 cursor-not-allowed'
                    : 'bg-[#3A7DFF] hover:bg-[#316BDF]'
                  }`}
                onClick={handleSubmit}
                disabled={files.length === 0}
              >
                Generate Flashcards
              </motion.button>
            )}

            {isProcessing && (
              <ProcessingLoader />
            )}
          </AnimatePresence>
        </div>

        <AnimatePresence>
          {isDownloadReady && (
            <DownloadSection />
          )}
        </AnimatePresence>
      </div>

      <KofiButton />
    </main>
  );
}