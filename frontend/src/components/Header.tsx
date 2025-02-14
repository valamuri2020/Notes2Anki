import { motion } from "framer-motion";

export default function Header() {
    return (
        <motion.header
            className="text-center relative"
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
        >
            <div className="absolute top-0 left-1/2 -translate-x-1/2 w-64 h-64 bg-blue-100 rounded-full filter blur-3xl opacity-20 -z-10" />
            <h1 className="text-6xl font-bold font-poppins tracking-wide">
                Notes2Anki
            </h1>
            <p className="mt-6 text-xl text-[#767676] max-w-2xl mx-auto leading-relaxed">
                Transform your study materials into powerful flashcards in seconds
            </p>
        </motion.header>
    );
}