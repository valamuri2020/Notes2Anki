"use client";

import { useState } from "react";
import { Toaster } from "react-hot-toast";
import { motion, AnimatePresence } from "framer-motion";
import FileUpload from "@/components/FileUpload";
import Header from "@/components/Header";
import CreativeLoader from "@/components/ProcessingLoader";
import DownloadSection from "@/components/DownloadSection";
import KofiButton from "@/components/KofiButton";

interface DownloadData {
  filename: string;
  blob: Blob;
  requestId: string;
}

export default function Home() {
  const [isProcessing, setIsProcessing] = useState(false);
  const [isDownloadReady, setIsDownloadReady] = useState(false);
  const [files, setFiles] = useState<File[]>([]);
  const [downloadData, setDownloadData] = useState<DownloadData | null>(null);

  const handleSubmit = async () => {
    if (files.length === 0) return;

    setIsProcessing(true);

    try {
      const formData = new FormData();
      files.forEach((file) => formData.append("files", file));

      // TODO: filename can be user specified...not for v0
      const requestData = {
        id: crypto.randomUUID(),
        anki_filename: "MyNotes"
      };

      formData.append("request", JSON.stringify(requestData));

      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/generate`, {
        method: "POST",
        body: formData,
      });

      const blob = await response.blob();
      const requestId = response.headers.get("X-Request-ID");

      setDownloadData({
        filename: "MyNotes",
        blob,
        requestId: requestId || ""
      });

      setIsProcessing(false);
      setIsDownloadReady(true);
    } catch (error) {
      console.error("Error generating deck:", error);
      setIsProcessing(false);
      setIsDownloadReady(false);
      alert("Error generating deck. Please try again later.");
    }
  };

  return (
    <main className="min-h-screen px-4 py-16">
      <div><Toaster position="top-right" reverseOrder={false} /></div>
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
                  Generate Deck ⚡️
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

          {isDownloadReady && downloadData && (
            <DownloadSection downloadData={downloadData} />
          )}
        </AnimatePresence>
      </div>

      <KofiButton />

      <footer className="mt-16 text-center text-sm text-gray-500">
        <p>No data is permanently stored. Made with ❤️. © {new Date().getFullYear()} Vivek Alamuri.</p>
      </footer>
    </main>
  );
}