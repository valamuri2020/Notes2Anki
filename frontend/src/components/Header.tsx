import { motion } from "framer-motion";

export default function Header() {
    return (
        <motion.header
            className="text-center relative mt-8"
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
        >
            <div className="absolute top-0 left-1/2 -translate-x-1/2 w-64 h-64 bg-blue-100 rounded-full filter blur-3xl opacity-20 -z-10" />
            <h1 className="text-7xl font-bold font-poppins tracking-wide">
                Notes2Anki
            </h1>
            <p className="mt-6 text-xl text-[#767676] max-w-2xl mx-auto leading-relaxed">
                Turn your slides into Anki cards. Built-in citations. No clutter.
            </p>
        </motion.header>
    );
}