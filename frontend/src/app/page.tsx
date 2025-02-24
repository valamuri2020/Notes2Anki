"use client";

import { useState, useEffect } from "react";
import { Toaster } from "react-hot-toast";
import { motion, AnimatePresence } from "framer-motion";
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

      console.log("API_URL: ", API_URL);
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
    <main className="min-h-screen px-4 py-16">
      <Toaster />
      <Header />
      <div className="max-w-4xl mx-auto mt-16">
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
                      Go ⚡️
                    </motion.button>
                  </div>
                  <div className="mt-9 p-2 border-2 border-dotted border-orange-500 rounded-lg bg-orange-100 text-center max-w-md mx-auto">
                    <p className="text-orange-800 text-sm">
                      This website is in alpha testing, stuff might break, please be patient. It's my first time :)
                    </p>
                  </div>
                </motion.div>
              )}

              {deckNamePhase && (
                <motion.div
                  key="deckname"
                  // initial={{ x: "-4%", opacity: 0 }}
                  // exit={{ x: "-10%", opacity: 0 }}
                  // Tween transition (smooth)
                  initial={{ opacity: 0, y: -20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.2 }}
                  className="flex flex-col items-center gap-4"
                >
                  <input
                    type="text"
                    placeholder="Enter deck name..."
                    value={deckName}
                    onChange={(e) => setDeckName(e.target.value)}
                    className="p-3 border rounded-lg w-full max-w-md"
                  />
                  <motion.button
                    whileHover={{ scale: 1.02 }}
                    whileTap={{ scale: 0.98 }}
                    className="bg-[#3A7DFF] hover:bg-[#316BDF] text-white px-8 py-3 rounded-lg text-lg font-medium transition-colors shadow-lg shadow-blue-500/20"
                    onClick={handleSubmit}
                  >
                    Generate Deck ⚡️
                  </motion.button>
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
    </main >
  );
}