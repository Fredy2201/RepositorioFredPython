select * from clientes
insert into clientes (nom_cli, tel_cli,nom_con,cond_cli)
values ('Katy MG','51940978478','Katy Guillen',1)


select * from servicios
SELECT cod_ser,des_ser,fec_ser,clientes.nom_cli,servicios.monto FROM servicios,clientes WHERE cond_ser=1 and servicios.cod_cli=clientes.cod_cli


select * from gastos

select * from deudas

select * from cobros


DELETE FROM servicios;
DELETE FROM sqlite_sequence WHERE name='servicios';