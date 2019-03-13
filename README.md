# Messaging Components (messaging_components)

## Description
Messaging components module is based on Abstract Messaging of Middleware [messaging_abstract](https://github.com/rh-messaging-qe/messaging_abstract).

# Objectives
- Brokers, Clients.. using "common API" -> AMOM
- Purpose for:
    - Messaging testing
    - Ansible module (future)
- Management
- Messaging product features (mainly for test coverage)

### Components
- Node
- Node Execution (Ansible, Executor)
- Protocols
    - AMQP (Priority for now)
    - MQTT (@TODO)
    - OpenWire (@TODO)
    - STOMP (@TODO)
- Authentication
    - NoAuth
    - SASL (@TODO)
    - SSL/TLS Cert based (@TODO)
- Brokers
    - ActiveMQ Artemis
    - Qpid
- Router
    - Qpid Dispatch
- Clients 
    - Internal CORE client (Python lib)
        - AMQP
            - Proton
    - CLI External 
        - AMQP
            - NodeJS
                - cli-rhea
            - Python
                - cli-proton
