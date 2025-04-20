// src/components/DownloadSection.tsx
import { motion } from "framer-motion";
import { Check, Download, Archive } from "lucide-react";
import { FEEDBACK_FORM_URL } from "@/lib/constants";
interface DownloadData {
    filename: string;
    blob: Blob;
    requestId: string;
    isZip?: boolean;
    files?: { name: string; size: number }[];
}

interface Props {
    downloadData: DownloadData;
    onDownloadClick: () => void;
}

export default function DownloadSection({ downloadData, onDownloadClick }: Props) {
    const fullFileName = downloadData.filename;
    const isZip = downloadData.isZip;

    return (
        <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            className="glass-morphism rounded-xl p-12 text-center relative overflow-hidden"
        >
            {/* Success checkmark animation */}
            <motion.div
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{
                    type: "spring",
                    stiffness: 200,
                    damping: 20
                }}
                className="mb-6"
            >
                <div className="w-16 h-16 bg-[#3A7DFF]/10 rounded-full flex items-center justify-center mx-auto">
                    <Check className="w-8 h-8 text-[#3A7DFF]" />
                </div>
            </motion.div>

            {/* Success message */}
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2 }}
            >
                <h2 className="text-2xl font-semibold mb-2">
                    Your flashcards are ready!
                </h2>
                <p className="text-[#767676] mb-8">
                    {isZip 
                        ? "Download your flashcard decks package below"
                        : "Download your Anki package below"
                    }
                </p>

                {/* File info */}
                <div className="mb-6 p-3 bg-white/50 rounded-lg inline-block">
                    {isZip ? (
                        <div>
                            <p className="text-sm text-[#767676] mb-2">
                                Package: {fullFileName}
                            </p>
                            <div className="text-left">
                                {downloadData.files?.map((file, index) => (
                                    <p key={index} className="text-xs text-[#767676] flex items-center gap-2">
                                        <Archive className="w-3 h-3" />
                                        {file.name}
                                    </p>
                                ))}
                            </div>
                        </div>
                    ) : (
                        <p className="text-sm text-[#767676]">
                            Package: {fullFileName}
                        </p>
                    )}
                </div>

                {/* Actions */}
                <div className="flex flex-col items-center gap-4">
                    <motion.button
                        whileHover={{ scale: 1.02 }}
                        whileTap={{ scale: 0.98 }}
                        className="bg-[#3A7DFF] hover:bg-[#316BDF] text-white px-8 py-3 rounded-lg 
                     flex items-center gap-2 font-medium transition-colors shadow-lg 
                     shadow-blue-500/20"
                        onClick={onDownloadClick}
                    >
                        <Download className="w-5 h-5" />
                        Download {isZip ? 'All Decks' : 'Now'}
                    </motion.button>

                    <a
                        href={FEEDBACK_FORM_URL}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-[#767676] hover:text-[#2C2C2C] hover:underline transition-colors text-sm"
                    >
                        Have feedback? Let us know ⭐️
                    </a>
                </div>
            </motion.div>
        </motion.div>
    );
}