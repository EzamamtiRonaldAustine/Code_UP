import { useState} from 'react';
import './App.css';
//component should be in capital letter
function Square() {
  const [name, setName] = useState(null);

  function handleButtonClick(){
    setName("X")
    console.log("Click action", name);

  }

  return <button onClick={handleButtonClick} className="square">{name}</button>;
}
function App() {
  return (
    <>
    <div className="board-row">
      <Square />
      <Square />
      <Square />
    </div>
    <div className="board-row">
      <Square />
      <Square />
      <Square />
    </div>
    <div className="board-row">
      <Square />
      <Square />
      <Square />
    </div>
    </>
  );
}

export default App;
