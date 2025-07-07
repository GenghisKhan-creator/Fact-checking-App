import react from "react";
import Header from "./Header";
import { FileUploadDemo } from "./Upload";

function Home () {
    return (
        <div className="text-gray-100">
            <Header/>
            <div className="h-[600px] flex flex-col justify-center items-center">
                <div className="py-10 text-5xl font-OpenSans font-bold">Hello, Ziyard!</div>
                <div><FileUploadDemo/></div>
            </div>
        </div>
    )
}

export default Home;