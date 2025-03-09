"use client";

import { useState, useEffect } from "react";
import { Toaster } from "react-hot-toast";
import { motion, AnimatePresence } from "framer-motion";
import Link from "next/link"; // Add this import
import FileUpload from "@/components/FileUpload";
import Header from "@/components/Header";
import CreativeLoader from "@/components/ProcessingLoader";
import DownloadSection from "@/components/DownloadSection";
import KofiButton from "@/components/KofiButton";
import { API_URL } from "@/lib/constants";
import { toast } from "react-hot-toast";

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
  const [deckNamePhase, setDeckNamePhase] = useState(false);
  const [deckName, setDeckName] = useState("");

  // Set default deck name from first uploaded file (without extension)
  useEffect(() => {
    if (files.length > 0 && !deckNamePhase && !deckName) {
      const defaultName = files[0].name.replace(/\.[^/.]+$/, "");
      setDeckName(defaultName);
    }
  }, [files, deckName, deckNamePhase]);

  const handleSubmit = async () => {
    if (!deckNamePhase) {
      if (files.length === 0) return;
      setDeckNamePhase(true);
      return;
    }

    if (!deckName.trim()) {
      toast.error("Please enter a deck name");
      return;
    }

    setIsProcessing(true);

    try {
      const formData = new FormData();
      files.forEach((file) => formData.append("files", file));

      const requestData = {
        id: crypto.randomUUID(),
        anki_filename: deckName + ".apkg"
      };

      formData.append("request", JSON.stringify(requestData));

      const response = await fetch(`${API_URL}/generate`, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const blob = await response.blob();
      const requestId = response.headers.get("X-Request-ID");

      setDownloadData({
        filename: deckName + ".apkg",
        blob,
        requestId: requestId || ""
      });

      setIsProcessing(false);
      setIsDownloadReady(true);
    } catch (error) {
      console.error("Error generating deck:", error);
      // Reset to initial state on error
      setDeckNamePhase(false);
      setIsProcessing(false);
      setIsDownloadReady(false);
      toast.error("Oops, there was an error: " + error);
    }
  };

  return (
    <main className="min-h-screen px-4 sm:px-6 py-8 sm:py-16 flex flex-col">
      <Toaster />
      <Header />
      <div className="max-w-4xl mx-auto mt-8 sm:mt-16 flex-grow w-full">
        <AnimatePresence mode="wait">
          {!isProcessing && !isDownloadReady && (
            <>
              {!deckNamePhase && (
                <motion.div
                  key="fileupload"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                >
                  <FileUpload
                    files={files}
                    setFiles={setFiles}
                  />

                  <div className="mt-6 sm:mt-8 flex justify-center">
                    <motion.button
                      whileHover={{ scale: 1.02 }}
                      whileTap={{ scale: 0.98 }}
                      className={`w-1/2 sm:w-auto px-6 sm:px-8 py-3 rounded-lg text-white text-base sm:text-lg font-medium 
                    transition-colors shadow-lg shadow-blue-500/20
                    ${files.length === 0
                          ? 'bg-neutral-400 cursor-not-allowed'
                          : 'bg-[#3A7DFF] hover:bg-[#316BDF]'
                        }`}
                      onClick={handleSubmit}
                      disabled={files.length === 0}
                    >
                      Next
                    </motion.button>
                  </div>
                  {/* <div className="mt-6 sm:mt-9 p-2 border-2 border-dotted border-orange-500 rounded-lg bg-orange-100 text-center max-w-md mx-auto">
                    <p className="text-orange-800 text-xs sm:text-sm">
                      This website is in alpha testing, stuff might break, please be patient. It&apos;s my first time.
                    </p>
                  </div> */}
                </motion.div>
              )}

              {deckNamePhase && (
                <motion.div
                  key="deckname"
                  initial={{ opacity: 0, y: -20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.2 }}
                  className="flex flex-col items-center gap-4 px-4 sm:px-0 w-full max-w-md mx-auto"
                >
                  <div className="w-full">
                    <label
                      htmlFor="deckName"
                      className="block text-base sm:text-lg font-medium text-[#2C2C2C] mb-2"
                    >
                      Deck Name
                    </label>
                    <input
                      id="deckName"
                      type="text"
                      placeholder="Enter deck name..."
                      value={deckName}
                      onChange={(e) => setDeckName(e.target.value)}
                      className="p-3 border rounded-lg w-full text-base sm:text-lg"
                    />
                  </div>
                  <div className="w-full flex justify-center mt-2">
                    <motion.button
                      whileHover={{ scale: 1.02 }}
                      whileTap={{ scale: 0.98 }}
                      className="w-1/2 sm:w-auto bg-[#3A7DFF] hover:bg-[#316BDF] text-white px-6 sm:px-8 py-3 rounded-lg text-base sm:text-lg font-medium transition-colors shadow-lg shadow-blue-500/20"
                      onClick={handleSubmit}
                    >
                      Generate Deck ⚡️
                    </motion.button>
                  </div>
                </motion.div>
              )}
            </>
          )}

          {isProcessing && (
            <motion.div
              key="processing"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="glass-morphism rounded-xl p-6 sm:p-12 flex justify-center"
            >
              <CreativeLoader />
            </motion.div>
          )}

          {isDownloadReady && downloadData && (
            <>
              <div className="flex justify-end mb-4">
                <Link
                  href="/"
                  className="text-sm text-[#767676] hover:text-[#2C2C2C] font-medium transition-colors flex items-center"
                >
                  Create Another &rarr;
                </Link>
              </div>
              <DownloadSection downloadData={downloadData} />
              <p className="text-xs text-[#767676] mt-6 text-center">AI can make mistakes. Please verify important information.</p>
            </>
          )}
        </AnimatePresence>
      </div>

      <KofiButton />

      <footer className="w-full mt-auto pt-8 pb-4 text-center text-xs sm:text-sm text-gray-500">
        <p>No data is permanently stored. Made with ❤️ by <a href="https://www.linkedin.com/in/valamuri/" target="_blank" rel="noopener noreferrer" className="hover:text-black underline transition-colors">Vivek Alamuri</a>.</p>
      </footer>
    </main>
  );
}