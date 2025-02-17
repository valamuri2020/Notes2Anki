import { motion } from "framer-motion";

export default function ProcessingLoader() {
    const numberOfCards = 8;
    const radius = 60; // radius of the circular path

    const cards = Array.from({ length: numberOfCards }, (_, i) => {
        const delay = i * 0.15; // stagger the animations

        return (
            <motion.div
                key={i}
                className="absolute w-10 h-14 border border-black rounded-md bg-white shadow-sm"
                animate={{
                    x: [
                        0,
                        radius * Math.cos((2 * Math.PI * i) / numberOfCards),
                        0
                    ],
                    y: [
                        0,
                        radius * Math.sin((2 * Math.PI * i) / numberOfCards),
                        0
                    ],
                    scale: [1, 0.8, 1],
                    opacity: [1, 0.6, 1],
                }}
                transition={{
                    duration: 3,
                    delay,
                    repeat: Infinity,
                    ease: "easeInOut",
                }}
            />
        );
    });

    return (
        <div className="flex flex-col items-center">
            <div className="relative h-40 w-40 mb-8">
                <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2">
                    {cards}
                </div>
            </div>

            <motion.div
                className="text-center"
                animate={{
                    opacity: [0.7, 1, 0.7],
                }}
                transition={{
                    duration: 2,
                    repeat: Infinity,
                    repeatType: "reverse",
                }}
            >
                <p className="text-lg text-[#2C2C2C] font-medium">
                    Converting your notes
                </p>
                <p className="text-sm text-[#767676] mt-2">
                    Grab some coffee...this might take a few minutes ☕️
                </p>
            </motion.div>
        </div>
    );
}
