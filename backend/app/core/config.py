"""
Hamary project me different configurations hon gi
environment variables, application name, Debug mode etc
agr hm ya configurations har python file me likhien gy tu code messy ho gay ga
Is liya hm centralized configuration file banaty han 
Is approach ko centralized configuration management kahty ha
Suppose hamara database password change ho jata hai 
agr password multiple lines me likha ho ga to har file update krna ho gi
lekin centralized coniguration mien sirf .env updtae krna ho ga
"""



from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    # Database Configuration
    DATABASE_URL: str

    # Application Configuration
    APP_NAME: str = "AI Recruitment Platform"
    DEBUG: bool = True

    # JWT Configuration
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"

    # Token Expiry
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    GROQ_API_KEY: str
    GROQ_MODEL: str = "llama-3.3-70b-versatile"

    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_EMAIL: str
    SMTP_PASSWORD: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()




#base settings pydantic ki class ha jo environment varaiables ko read aur vaidate krnae me help krti ha
#settingconfigDict pydantic ko bata ha configuration kaha sae load krni ha