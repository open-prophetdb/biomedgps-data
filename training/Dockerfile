
FROM pytorch/pytorch:1.13.1-cuda11.6-cudnn8-runtime

# Add your customizations here

# Example: Install additional packages
RUN apt-get update && apt install git -y
RUN pip install --no-cache-dir torchvision && pip install git+https://github.com/yjcyxky/dgl-ke#subdirectory=python && pip install ogb dgl==0.9.0 wandb
COPY . /opt/biomedgps-kge
RUN chmod +x /opt/biomedgps-kge/train.sh

# Example: Set the working directory
WORKDIR /data/biomedgps-kge

# Example: Run your application
CMD ["bash", "-c", "/opt/biomedgps-kge/train.sh"]
