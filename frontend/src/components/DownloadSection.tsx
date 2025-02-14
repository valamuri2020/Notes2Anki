import { motion } from "framer-motion";

export default function DownloadSection() {
    return (
        <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 20 }}
            className="mt-12 bg-white rounded-lg p-6 shadow-sm text-center"
        >
            <h2 className="text-xl font-semibold mb-4">
                Your Anki package is ready to download!
            </h2>
            <button
                onClick={() => {
                    // TODO: Implement actual download
                    alert("Download functionality will be implemented");
                }}
                className="bg-[#3A7DFF] hover:bg-[#316BDF] text-white px-6 py-2 rounded-lg transition-colors"
            >
                Download Package
            </button>
            <button
                className="ml-4 text-[#2C2C2C] hover:text-[#316BDF] transition-colors"
                onClick={() => {
                    // TODO: Implement sharing functionality
                    alert("Share functionality will be implemented");
                }}
            >
                Share with others
            </button>
        </motion.div>
    );
}
