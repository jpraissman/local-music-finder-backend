import dotenv
import os

dotenv_file = dotenv.find_dotenv()
dotenv.load_dotenv(dotenv_file)

print(os.environ["TEST"])
os.environ["TEST"] = "New Value"
print(os.environ["TEST"])

dotenv.set_key(dotenv_file, "TEST", "Newest Value")